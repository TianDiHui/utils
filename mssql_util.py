# -*- coding: utf-8 -*-

"""
sql server 操作类

:param param1: this is a first param
:param param2: this is a second param
:returns: this is a description of what is returned
:raises keyError: raises an exception
@author： jhuang
@time：12/04/2018
"""

# server = "192.168.10.2"
# user = "sa"
# password = "Sbh2017"
# database = "ecology"
# mssql=MSSQL(server,user,password,database)
# print mssql.query('select @@version')
# mssql.close()

import pymssql


class MSSQL:
    def __init__(self, host, user, pwd, db):  # 类的构造函数，初始化数据库连接ip或者域名，以及用户名，密码，要连接的数据库名称
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):  # 得到数据库连接信息函数， 返回: conn.cursor()
        if not self.db:
            raise (NameError, "未设置数据库信息")
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset='utf8')
        cur = self.conn.cursor()  # 将数据库连接信息，赋值给cur。
        if not cur:
            raise (NameError, "连接数据库失败")
        else:
            return cur

    # 执行查询语句,返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
    def query(self, sql):  # 执行Sql语句函数，返回结果
        cur = self.__GetConnect()  # 获得数据库连接信息
        cur.execute(sql)  # 执行Sql语句
        rows_list = cur.fetchall()  # 获得所有的查询结果
        colNameList = []
        col_name_index=1
        for i in range(len(cur.description)):
            col_name = cur.description[i][0]
            if col_name in colNameList:
                col_name='%s_%s' %(col_name,col_name_index)
                col_name_index=+1
            colNameList.append(col_name)

            # colNames = ','.join(colNameList)
        rows_list_2 = []
        for row in rows_list:  # 遍历每一行
            dict = {}
            n = 0

            # print len(rows_list)
            # print len(rows_list_2)
            for col_value in row:  # 遍历每一行的列
                col_name = colNameList[n]

                dict[col_name] = col_value
                n += 1
            rows_list_2.append(dict)
        # print rows_list_2
        return rows_list_2

    def execute(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)

    def __del__(self):
        self.close()

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()
