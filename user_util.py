# -*- coding: utf-8 -*-


class UserObj(object):
    """
    用户信息基类

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：02/08/2018
    """

    def __init__(self):
        self.userid = None
        self.user_id = None
        self.role_id = None
        self.user_email = None
        self.role_auth_level = None
        self.username = None
        self.hospital_code = None
        self.user_nick = None
        self.nick = None
        self.password = None
        self.password_org = None
