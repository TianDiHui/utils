# -*- coding: utf-8 -*-

#
# connect()方法用于连接数据库，返回一个数据库连接对象。如果要连接一个位于host.remote.com服务器上名为fourm的MySQL数据库，连接串可以这样写：
# db = MySQLdb.connect(host="remote.com",user="user",passwd="xxx",db="fourm" )
# connect()的参数列表如下：
# host，连接的数据库服务器主机名，默认为本地主机(localhost)。
# user，连接数据库的用户名，默认为当前用户。
# passwd，连接密码，没有默认值。
# db，连接的数据库名，没有默认值。
# conv，将文字映射到Python类型的字典。默认为MySQLdb.converters.conversions
# cursorclass，cursor()使用的种类，默认值为MySQLdb.cursors.Cursor。
# compress，启用协议压缩功能。
# named_pipe，在windows中，与一个命名管道相连接。
# init_command，一旦连接建立，就为数据库服务器指定一条语句来运行。
# read_default_file，使用指定的MySQL配置文件。
# read_default_group，读取的默认组。
# unix_socket，在unix中，连接使用的套接字，默认使用TCP。
# port，指定数据库服务器的连接端口，默认是3306。
# 连接对象的db.close()方法可关闭数据库连接，并释放相关资源。
# 连接对象的db.cursor([cursorClass])方法返回一个指针对象，用于访问和操作数据库中的数据。
# 连接对象的db.begin()方法用于开始一个事务，如果数据库的AUTOCOMMIT已经开启就关闭它，直到事务调用commit()和rollback()结束。
# 连接对象的db.commit()和db.rollback()方法分别表示事务提交和回退。
# 指针对象的cursor.close()方法关闭指针并释放相关资源。
# 指针对象的cursor.execute(query[,parameters])方法执行数据库查询。
# 指针对象的cursor.fetchall()可取出指针结果集中的所有行，返回的结果集一个元组(tuples)。
# 指针对象的cursor.fetchmany([size=cursor.arraysize])从查询结果集中取出多行，我们可利用可选的参数指定取出的行数。
# 指针对象的cursor.fetchone()从查询结果集中返回下一行。
# 指针对象的cursor.arraysize属性指定由cursor.fetchmany()方法返回行的数目，影响fetchall()的性能，默认值为1。
# 指针对象的cursor.rowcount属性指出上次查询或更新所发生行数。-1表示还没开始查询或没有查询到数据。
import collections
import datetime
import json
import time

import MySQLdb
import pymysql
from django.core import serializers
from django.db import connection

logger = logging.getLogger('django')


def sql_to_list(sql, args=None, print_sql=False):
    """
    | ##@函数目的: SQL结果到json
    | ##@参数说明：
    | ##@返回值：包含json串数组
    | ##@函数逻辑：paramList 列表
    | ##@开发人：jhuang
    | ##@时间：
    示例:
        try:
            if request.method == 'GET':
                arrays=sql_to_list('select a.*,b.hospital_code from dbscript_req a ,dbscript_req_hospital b where a.dbscript_event_id=b.dbscript_event_id')
                return http_response_json(arrays,True)
        except Exception,e:
            return http_response_json("操作失败:%s" %(get_except(e)))

    """
    sql_2_list = Sql2List()
    lst = sql_2_list.sql_to_list(sql, args, print_sql)
    sql_2_list.close()
    return lst


class Sql2List():
    """
    | ##@函数目的: Sql2List
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    def __init__(self):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.host = None
        self.user_name = None
        self.pwd = None
        self.db_name = None
        self.port = None

    def custom_connect(self, host, user_name, pwd, db_name, port):
        self.host = host
        self.user_name = user_name
        self.pwd = pwd
        self.db_name = db_name
        self.port = db_name
        self.connection = pymysql.connect(host, user_name, pwd, db_name, port=port, charset='utf8')
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()

    # def sql_to_queryset_and_dic(self, sql, args=None, print_sql=True):
    def sql_to_queryset_and_dic(self, sql, args=None, print_sql=False):
        # 返回一个查询结果集对象
        if isinstance(args, list) is False and args is not None:
            lists = []
            lists.append(args)
            args = lists
        tstart = time.time()

        rownum = self.cursor.execute(sql, args)
        lists_queryset = []
        lists_dict = []
        datas = self.cursor.fetchall()
        if rownum > 0:
            for obj in datas:
                dic = {}
                i = 0
                row_queryset = RowQueryset()
                for field_desc in self.cursor.description:
                    col = field_desc[0]  # 列
                    rowValue = obj[i]  # 值
                    dic[col] = rowValue
                    setattr(row_queryset, col, rowValue)  # 动态为对象添加属性
                    i += 1
                lists_queryset.append(row_queryset)
                lists_dict.append(dic)

            if print_sql:
                logger.debug('%s\nSQL参数: %s\nSQL用时:%s\n结果集数:%s' % (sql, args, time.time() - tstart, len(datas)))
            return lists_queryset, lists_dict
        else:
            return lists_queryset, lists_dict

    # def sql_to_queryset(self, sql, args=None, print_sql=True):
    def sql_to_queryset(self, sql, args=None, print_sql=False):
        # 返回一个查询结果集对象
        if isinstance(args, list) is False and args is not None:
            lists = []
            lists.append(args)
            args = lists
        tstart = time.time()

        rownum = self.cursor.execute(sql, args)
        lists_queryset = []
        lists_dict = []
        datas = self.cursor.fetchall()
        if rownum > 0:
            for obj in datas:
                dic = {}
                i = 0
                row_queryset = RowQueryset()
                for field_desc in self.cursor.description:
                    col = field_desc[0]  # 列
                    rowValue = obj[i]  # 值
                    setattr(row_queryset, col, rowValue)  # 动态为对象添加属性
                    i += 1
                lists_queryset.append(row_queryset)

            if print_sql:
                logger.debug('%s\nSQL参数: %s\nSQL用时:%s\n结果集数:%s' % (sql, args, time.time() - tstart, len(datas)))
            return lists_queryset
        else:
            return lists_queryset

    def sql_to_list(self, sql, args=None, print_sql=False):

        if isinstance(args, list) is False and args is not None:
            lists = []
            lists.append(args)
            args = lists
        tstart = time.time()

        rownum = self.cursor.execute(sql, args)
        lists = []
        datas = self.cursor.fetchall()
        if rownum > 0:
            for obj in datas:
                dic = collections.OrderedDict()
                i = 0
                for field_desc in self.cursor.description:
                    col = field_desc[0]  # 列
                    rowValue = obj[i]  # 值
                    dic[col] = rowValue
                    i += 1
                lists.append(dic)

            if print_sql:
                logger.debug('%s\nSQL参数: %s\nSQL用时:%s\n结果集数:%s' % (sql, args, time.time() - tstart, len(datas)))
            return lists
        else:
            return lists

    def execute(self, sql, args=None, print_sql=False):
        if print_sql:
            logger.debug('%s ->参数: %s' % (sql, args))
        self.cursor.execute(sql, args)
        return self.cursor

    # def execute_many(self, sql, args, print_sql=True):
    def execute_many(self, sql, args, print_sql=False):
        """
        批量插入
        sql2list.execute_many("insert {tmp_table_name} (word) values(%s)".format(tmp_table_name=tmp_table_name) ,insert_value_list)


        :param param1: sql， 比如：'insert into 表名(a,b) value(%s,%s)'
        :param param2: args 需要插入的字段值的元祖列表集合 比如：[(a1,b1),(a2,b2)]
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：9/11/2018
        """
        self.cursor.executemany(sql, args)
        tstart = time.time()
        if print_sql:
            logger.debug('%s\nSQL参数: %s\nSQL用时:%s\ninsert数:%s' % (sql, args, time.time() - tstart, len(args)))


class RowQueryset():
    """
    描述

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：09/08/2018
    """

    def __init__(self):
        pass


def wrapper_dbconnect_custom(host, user_name, pwd, db_name):
    """
        装饰器，自定义数据库连接

        :param param1: this is a first param
        :param param2: this is a second param
        :returns:
        :raises keyError: raises an exception
        @author： jhuang
        @time：08/02/2018
    """

    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            db = MySQLdb.connect(host, user_name, pwd, db_name, charset='utf8')
            ret = func(*args, **kwargs)

            return ret

        return inner_wrapper

    return wrapper


def sql_exec(sql, args=None, print_sql=False):
    """
    | ##@函数目的:执行SQL
    | ##@参数说明：
    | ##@返回值：tuple
    | ##@函数逻辑：paramList 列表
    | ##@开发人：jhuang
    | ##@时间：
    """
    if print_sql:
        logger.debug('%s ->参数: %s' % (sql, args))
    cursor = connection.cursor()
    cursor.execute(sql, args)
    # cursor.close()
    return cursor


def queryset_to_json(queryset_object):
    """
    | ##@函数目的: 将模型QUERYSET对象转化（序列化）为JSON
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@
    """
    json_obj = json.loads(serializers.serialize("json", queryset_object))
    # logger.debug(json_obj)
    return json_obj


# 以下不推荐使用
# ==========================================================================
def sql_to_tuple(sql, args=None, print_sql=False):
    """
    | ##@函数目的: SQL结果到数组
    | ##@参数说明：
    | ##@返回值：tuple
    | ##@函数逻辑：paramList 列表
    | ##@开发人：jhuang
    | ##@时间：
    """

    if print_sql is True:  logger.debug(u'%s ->参数: %s' % (sql, args))
    cursor = connection.cursor()
    cursor.execute(sql, args)
    tuples = cursor.fetchall()
    # cursor.close()
    return tuples


def sql_to_dict(sql, args=None, print_sql=False):
    """
    |##@函数目的：SQL结果到一个dic中，用于根据不同条件循环SQL，后面加入到一个大的数组中，这个之返回一条记录
    |##@参数说明：
    |##@返回值：obj 用于添加到一个数组中
    |##@函数逻辑：
    |##@开发人：runksun
    |##@时间：2017年2月6日

        示例:
            try:
                if request.method == 'GET':
                    arrays = []
                    dic=sql_to_list('select a.*,b.hospital_code from dbscript_req a ,dbscript_req_hospital b where a.dbscript_event_id=b.dbscript_event_id')
                    arrays.append(dic)
                    return http_response_json(arrays,True)
            except Exception,e:
                return http_response_json("操作失败:%s" %(get_except(e)))

    """
    if isinstance(args, list) == False and args != None:
        lists = []
        lists.append(args)
        args = lists

    tstart = time.time()
    if print_sql:    logger.debug('%s\n参数: %s' % (sql, args))
    cursor = connection.cursor()
    rownum = cursor.execute(sql, args)
    datas = cursor.fetchall()
    # logger.debug datas
    dic = {}
    if rownum > 0:

        i = 0
        for field_desc in cursor.description:
            col = field_desc[0]
            rowValue = datas[0][i]
            # 转换时间格式
            if isinstance(rowValue, datetime.datetime):
                rowValue = rowValue.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(rowValue, str):
                rowValue = str(rowValue)
            if isinstance(rowValue, long):
                rowValue = str(rowValue)
            dic[col] = rowValue
            i += 1
        cursor.close()
        if print_sql:   logger.debug('参数: %s\n用时:%s\n返回结果数量:%s' % (args, time.time() - tstart, len(datas)))
        return dic
    else:
        return dic


def django_query_debug():
    """
    |##@函数目的：打印django模型SQL语句和相关信息，用于调试
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：jhuang
    |##@时间：
    """
    logger.debug(connection.queries)


def make_sure_mysql_usable(func):
    """
    装饰器，确保数据库连接可用，不可用重新连接

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：09/02/2018
    """

    def wrapper(*args, **kargs):
        # 确保数据库连接可用，防止连接被服务端主动关闭情况下的异常
        # 参考 https://stackoverflow.com/questions/7835272/django-operationalerror-2006-mysql-server-has-gone-away
        from django.db import connection, connections
        for conn in connections.all():
            conn.close_if_unusable_or_obsolete()
        # mysql is lazily connected to in django.
        # connection.connection is None means
        # you have not connected to mysql before
        for i in range(1, 6):

            if connection.connection and not connection.is_usable():
                logger.debug('MYSQL连接不可用，删除连接，重新申请(第%s次)! %s' % (i, func.__name__))
                # destroy the default mysql connection
                # after this line, when you use ORM methods
                # django will reconnect to the default mysql
                del connections._connections.default
            if connection.connection and connection.is_usable():
                logger.debug('MYSQL连接可用，申请成功(第%s次)! %s' % (i, func.__name__))
                break

        return func(*args, **kargs)

    return wrapper
