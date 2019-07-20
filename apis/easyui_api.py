# -*- coding: utf-8 -*-
from django.views import View

from ..common_util import response_json, view_except
from ..db_util import sql_to_list


class ComboboxAPI():

    # @view_except()
    def query_sys_code(self, request):
        """
        码表查询通用接口
        url:'/sys/query_sys_code?sys_code_type=project_type,project_hour_submited,project_type_myself&select_code',

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：11/05/2018
        """
        sys_code_type = request.GET.get('sys_code_type')  # 查询那些类型的sys_code_type
        select_code = request.GET.get('select_code')  # 前台默认选择的sys_code
        exclude_code = request.GET.get('exclude_code', '')  # 排除不需要的sys_code
        insert_all = request.GET.get('insert_all', '')  # 逻辑增加 sys_code_type = xx 的“全部”sys_code
        sys_code_type = str(sys_code_type).split(',')
        exclude_code = str(exclude_code).split(',')
        param_list = sys_code_type + exclude_code

        sql = """SELECT * FROM sys_code WHERE sys_code_type in ( %s) and sys_code not in(%s) and (status = '1' or status is NULL) order by order_index""" % (
            ','.join(
                ['%s'] * len(sys_code_type)), ','.join(['%s'] * len(exclude_code)))
        project_account_lists = sql_to_list(sql, param_list)
        for r in project_account_lists:
            if r['sys_code'] == select_code:
                r['selected'] = 'true'

        if insert_all == 'yes':
            has_all = False
            for i in sys_code_type:
                for j in project_account_lists:
                    if j['sys_code'] == '':
                        has_all = True
                not has_all and project_account_lists.insert(0, {'sys_code': '', 'sys_code_text': '全部', 'sys_code_type': i})

        return response_json(project_account_lists)
