# -*- coding: utf-8 -*-


# http://www.oracle.com/technetwork/articles/dsl/python-091105.html

# 官方网站：https://oracle.github.io/python-cx_Oracle/

# oracle 数据库操作封装
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# db_info = {
#         'dbtype':'oracle',
#         'user':'thdba',
#         'pwd':'thzk',
#         'host':'192.168.220.90',
#         'port':'1521',
#         'sid':'orcl'
#     }
# ora = Ora(db_info = db_info)
# rows = ora.query("""select sum(bytes) bytes
# from dba_segments
# where owner = 'EMR'
# and segment_type not in (
#    'CACHE',
#    'ROLLBACK',
#    'TYPE2',
#    'UNDO',
#    'INDEX'
# )""")
# print   ( rows[0]['bytes'])
#
# ora.close()

# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import collections
import logging

import cx_Oracle
from DBUtils.PooledDB import PooledDB

from SRMCenter.apps.global_var import GlobalVar
logger = logging.getLogger('django')
from utils.crypto_util import pwd_help


def oracle_pwd_decrypt(function):
    def wrapper(db_info):
        try:
            if db_info.has_key('pwd'):
                pwd_str = pwd_help(db_info['pwd'], GlobalVar.string_crypt)
                db_info['pwd'] = pwd_str
                return function(db_info)
            return function(db_info)
        except Exception as e:
            logger.error('oracle_pwd_decrypt error ' + str(e.message))
            raise
    return wrapper


class Ora():
    __pool = None  # 连接池对象

    def __init__(self, db_info=None):

        self.db_info = db_info

        self.conn = Ora.__getConn(self.db_info)
        self.cursor = self.conn.cursor()

    @staticmethod
    @oracle_pwd_decrypt
    def __getConn(db_info):

        # 静态方法，从连接池中取出一个连接
        if Ora.__pool is None:
            print '新开启一个oracle数据库连接...'
            __pool = PooledDB(cx_Oracle,
                              user=db_info['user'],
                              password=db_info['pwd'],
                              dsn="%s:%s/%s" % (db_info['host'], db_info['port'], db_info['sid']),
                              mincached=20,
                              maxcached=200)
        return __pool.connection(shareable=False)

    # 查询表的所有列
    def columns(self, table):
        sql = ["select lower(column_name)column_name \
        from user_tab_columns where table_name=upper('%(table)s')"]
        rows = self.query(''.join(sql) % locals())
        col_list = [k["column_name"] for k in rows]
        # ['sjhm', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'status']
        return col_list

    # 根据表自动创建参数字典
    def create_params(self, table, args={}):
        col_list = self.columns(table)
        params = {}
        for k in col_list:
            if args.has_key(k):
                params[k] = args[k]
        return params

    # 执行sql
    def execute(self, sql, args={}):

        self.cursor.execute(sql, args)

    # 批量执行
    def executemany(self, sql, args):
        try:
            return self.cursor.executemany(sql, args)
        except Exception as e:
            # self.close()
            raise e

    # 备份记录,如果没有该表格将自动建表，以log_表名 命名,参数二：操作人工号，参数三：操作说明，
    # 参数四：用于where条件，如 where 字段3=值3 and 字段4=值4，格式{'字段3':'值3','字段4':'值4'}
    def backup(self, table, userid, remark, cond_dict):
        cond_dict = self.create_params(table, cond_dict)
        sql = ["select count(*)cnt FROM user_tables "]
        sql.append(" WHERE table_name = upper('log_%(table)s')")
        rows = self.query("".join(sql) % locals())
        if rows[0]["cnt"] == 0:  # 注意oracle列名大写
            self.execute("create table log_%(table)s as  select * from %(table)s where 1>2 " % locals())
            self.execute(" alter table log_%(table)s add(backup_userid varchar2(40),\
            backup_date date,back_remark varchar2(200))" % locals())
        cond_stmt = ' and '.join(['%s=:%s' % (k, k) for k in cond_dict.keys()])
        upd_sql = "insert into log_%(table)s select t.*,:userid,sysdate,:remark from %(table)s t where %(cond_stmt)s"
        cond_dict['userid'] = userid
        cond_dict['remark'] = remark
        return self.execute(upd_sql % locals(), cond_dict)

    # 执行sql，参数一：sql语句，参数二：参数字典{'字段1'：'值1','字段2':'值2'}
    def query(self, sql, args={}):
        logger.debug(sql)
        self.execute(sql, args)

        rows = self.get_rows()
        # print rows
        return rows

    # 分页查询，参数一：sql语句，参数二：参数字典{'字段1'：'值1','字段2':'值2'}，参数三：页码，参数四：分页大小
    def query_pages(self, sql, args={}, page=1, page_size=30):
        _args, count_args = args, args
        page = int(page)
        # logger.info  ( "page:%s" %(page,)
        # 下一页
        next_page = page_size * page
        # 当前页
        cur_page = page_size * (page - 1)
        if page == 1 or cur_page < 0:
            cur_page = 1
            next_page = page_size
        else:
            cur_page = cur_page + 1
        orderby = ''

        # parser = OracleStatementParser(sql)
        # statement = parser.parseStatement()
        # visitor = OracleSchemaStatVisitor()
        # statement.accept(visitor)
        # # print visitor.getTables()
        # getColumns_list = visitor.getColumns()

        if 'order by ' not in str(sql).lower():
            orderby = ''
        sql = """SELECT * FROM(
               SELECT ROWNUM RNRNRN,T.* FROM(""" + sql + """ %s )T 
               WHERE ROWNUM<=:next_page
               )WHERE RNRNRN >=:cur_page  """ % (orderby)

        _args["cur_page"] = cur_page
        _args["next_page"] = next_page
        rows = self.query(sql, _args)
        list_column = [i[0] for i in self.cursor.description]  # 解决列排序不正确的问题

        return [rows, len(rows), list_column]

    # oracle的参数名必须使用:代替，如 userid = :userid
    def insert(self, table, column_dict):
        column_dict = self.create_params(table, column_dict)
        keys = ','.join(column_dict.keys())
        values = column_dict.values()
        placeholder = ','.join([':%s' % (v) for v in column_dict.keys()])
        ins_sql = 'INSERT INTO %(table)s (%(keys)s) VALUES (%(placeholder)s)'
        self.execute(ins_sql % locals(), column_dict)

    # 获取序列的下一个值，传入sequence的名称
    def nextval(self, seq):
        self.cursor.execute("SELECT %(seq)s.nextval from dual " % locals())
        result = self.cursor.fetchall()
        return result[0][0]

    # 批量插入数据库，参数一：表名，参数二：['字段1','字段2',...],参数二：[('值1','值2',...),('值1','值2',...)]
    def multi_insert(self, table, columns=[], values=()):
        keys = ','.join(columns)
        placeholder = ','.join([':%s' % (v) for v in columns])
        ins_sql = 'INSERT INTO %(table)s (%(keys)s) VALUES(%(placeholder)s)'
        return self.cursor.executemany(ins_sql % locals(), values)

    # 更新，参数一：表名，参数二用于set 字段1=值1，字段2=值2...格式：{'字段1':'值1','字段2':'值2'},
    # 参数三：用于where条件，如 where 字段3=值3 and 字段4=值4，格式{'字段3':'值3','字段4':'值4'}
    def update(self, table, column_dict={}, cond_dict={}):
        column_dict = self.create_params(table, column_dict)
        cond_dict = self.create_params(table, cond_dict)
        set_stmt = ','.join(['%s=:%s' % (k, k) for k in column_dict.keys()])
        cond_stmt = ' and '.join(['%s=:%s' % (k, k) for k in cond_dict.keys()])
        upd_sql = 'UPDATE %(table)s set %(set_stmt)s where %(cond_stmt)s'
        args = dict(column_dict, **cond_dict)  # 合并成1个
        return self.execute(upd_sql % locals(), args)

    # 删除，参数一：表名，#参数二：用于where条件，如 where 字段3=值3 and 字段4=值4，格式{'字段3':'值3','字段4':'值4'}
    def delete(self, table, cond_dict):
        cond_dict = self.create_params(table, cond_dict)
        cond_stmt = ' and '.join(['%s=:%s' % (k, k) for k in cond_dict.keys()])
        del_sql = 'DELETE FROM %(table)s where %(cond_stmt)s'
        return self.execute(del_sql % locals(), cond_dict)

    # 提取数据，参数一提取的记录数，参数二，是否以字典方式提取。为true时返回：{'字段1':'值1','字段2':'值2'}
    def get_rows(self, size=None, is_dict=True):
        self.query_rows_data_list = []

        if size is None:
            rows = self.cursor.fetchall()
        else:
            rows = self.cursor.fetchmany(size)
        if rows is None:
            rows = []
        if is_dict:
            list_rows = []

            dict_keys = [r[0].lower() for r in self.cursor.description]
            for row in rows:
                list_rows.append(collections.OrderedDict((zip(dict_keys, row))))
                row = row[1:]
                self.query_rows_data_list.append(row)
            rows = list_rows
        return rows

    # 获取记录数
    def get_rows_num(self):
        return self.cursor.rowcount

    # 提交
    def commit(self):
        self.conn.commit()

    # 取消
    def cancel(self):
        self.conn.cancel()
        # self.cursor.close()

    # 回滚
    def rollback(self):
        self.conn.rollback();

    # 销毁,创建对象后，一般是进程结束的时候，python解释器默认调用__init__()方法。当删除一个对象时，python解释器也会默认调用一个方法，这个方法为__del__()方法。在python中，对于开发者来说很少会直接销毁对象(如果需要，应该使用del关键字销毁)。Python的内存管理机制能够很好的胜任这份工作。也就是说,不管是手动调用del还是由python自动回收都会触发__del__方法执行:
    def __del__(self):
        # pass
        print '实例销毁！关闭'
        self.close_cursor()
        self.close_connect()

    # 关闭连接(可以用于关闭upate)
    def close_cursor(self):
        # pass
        self.rollback()
        self.cursor.close()

    def close_connect(self):
        self.conn.close()
