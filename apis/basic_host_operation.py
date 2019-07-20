# -*- coding: utf-8 -*-
import re

from ..common_util import response_json, view_except
from ..db_util import sql_to_list
from SRMCenter.apps.global_var import GlobalVar


def query_hots_login_permission_information(server_id):
    """
    查询服务器相关权限
    :param server_id:
    :return:
    liww
    """
    sql = """
    SELECT a.server_ip,a.server_name,a.server_port,a.server_user,a.server_pwd
    FROM server_instance a
    WHERE a.server_id = '%s'
    """ %server_id

    sql_list = sql_to_list(sql)

    test=re.findall('\^_\^(.*?)\^_\^', sql_list[0]['server_pwd'])

    server_pwd = GlobalVar.string_crypt.decrypt(test[0])

    sql_list[0]['server_pwd'] = server_pwd

    return sql_list


def query_current_userid(request):
    """
    查询当前登陆用户的userid
    :param server_id:
    :return:
    liww
    """

    userid = request.session['userid']

    return response_json(userid)
