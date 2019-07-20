import collections
import time

import pymysql


class MySQL:
    __db = None

    # 在这里配置自己的SQL服务器

    def __init__(self, config):
        self.config = config

        self.__connect()

    def __del__(self):
        if (self.__db is not None):
            self.__db.close()

    def __connect(self):
        if (self.__db == None):
            self.__db = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['username'],
                passwd=self.config['password'],
                db=self.config['database'],
                charset=self.config['charset']
            )
        return self.__db

    def sql_to_list(self, sql, args=None, print_sql=False):

        if isinstance(args, list) is False and args is not None:
            lists = []
            lists.append(args)
            args = lists
        tstart = time.time()

        cursor = self.__connect().cursor()

        rownum = cursor.execute(sql, args)
        lists = []
        datas = cursor.fetchall()
        if rownum > 0:
            for obj in datas:
                dic = collections.OrderedDict()
                i = 0
                for field_desc in cursor.description:
                    col = field_desc[0]  # 列
                    rowValue = obj[i]  # 值
                    dic[col] = rowValue
                    i += 1
                lists.append(dic)

            if print_sql:
                print('%s\nSQL参数: %s\nSQL用时:%s\n结果集数:%s' % (sql, args, time.time() - tstart, len(datas)))
            return lists
        else:
            return lists

    def query(self, _sql):
        cursor = self.__connect().cursor()
        try:
            cursor.execute(_sql)
            data = cursor.fetchall()
            # 提交到数据库执行
            self.__connect().commit()
        except:
            # 如果发生错误则回滚
            self.__connect().rollback()
            return False
        return data

    def query_dic(self, _sql_dic):
        if ('select' in _sql_dic.keys()):
            sql = "SELECT " + _sql_dic['select'] + " FROM " + _sql_dic['from'] + self.where(_sql_dic['where'])
            print(sql)
            return self.query(sql)
        elif ('insert' in _sql_dic.keys()):
            sql = "INSERT INTO " + _sql_dic['insert'] + self.quote(_sql_dic['domain_array'],
                                                                   type_filter=False) + " VALUES " + self.quote(
                _sql_dic['value_array'])
            print(sql)
            return self.query(sql)
        if ('delete' in _sql_dic.keys()):
            sql = "DELETE FROM " + _sql_dic['delete'] + self.where(_sql_dic['where'])
            print(sql)
            return self.query(sql)

    def where(self, _sql):
        if (isinstance(_sql, dict) == False):
            return " WHERE " + str(_sql)
        if (isinstance(_sql, dict)):
            _sql_dic = _sql
            s = " WHERE "
            index = 0
            for domain in _sql_dic:
                if (index == 0):
                    s += domain + "=" + str(_sql_dic[domain]) + " "
                    index += 1
                else:
                    s += "AND " + domain + "=" + str(_sql_dic[domain]) + " "
            return s

    # 为数组加上外括号，并拼接字符串
    def quote(self, _data_array, type_filter=True):
        s = "("
        index = 0
        if (type_filter):
            for domain in _data_array:
                if (index == 0):
                    if (isinstance(domain, int)):
                        s += str(domain)
                    elif (isinstance(domain, str)):
                        s += "'" + domain + "'"
                    index += 1
                else:
                    if (isinstance(domain, int)):
                        s += ", " + str(domain)
                    elif (isinstance(domain, str)):
                        s += ", " + "'" + domain + "'"
        else:
            for domain in _data_array:
                if (index == 0):
                    s += str(domain)
                    index += 1
                else:
                    s += ", " + domain
        return s + ")"
