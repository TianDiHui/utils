# -*- coding: utf-8 -*-
'''
@author: lanxiong lanxiong@cenboomh.com
@file: syscode_utils.py.py
@time: 2018/10/24 14:58
@desc:
'''

from .db_util import Sql2List


class SysCodeUtils(object):
    def __init__(self):
        self.obj_query = Sql2List()

    def get_syscode_list(self, sysc_ode_type_list, only_get_code=False):
        type_str = ", ".join(map(lambda x: "'%s'" % x, sysc_ode_type_list))
        if only_get_code:
            sql = """
            select sys_code from sys_code where sys_code_type in ({})
            """.format(type_str)
        else:
            sql = """
            select * from sys_code where sys_code_type in ({})
            """.format(type_str)

        queryset = self.obj_query.sql_to_list(sql)
        self.obj_query.close()
        return queryset

    def has_syscode(self, sys_code_type, sys_code):
        sql = """
        select sys_code from sys_code where sys_code_type='{}' and sys_code = '{}'
        """.format(sys_code_type, sys_code)
        queryset = self.obj_query.sql_to_list(sql)
        self.obj_query.close()
        if queryset:
            return True
        else:
            return False