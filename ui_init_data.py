# -*- coding: utf-8 -*-
'''
@author: lanxiong lanxiong@cenboomh.com
@file: ui_init_data.py
@time: 2018/12/6 21:19
@desc:
'''
from django.core.exceptions import FieldError

from ..models.models import UserAccount, UserRoleIdList
import datetime


class User(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.set_obj()

    def set_obj(self):
        try:
            qset_obj_user = UserAccount.objects.filter(user_id=self.user_id).values()
        except FieldError:
            qset_obj_user = UserAccount.objects.filter(userid=self.user_id).values()

        if qset_obj_user:
            for i in qset_obj_user:
                for k, v in i.iteritems():
                    if isinstance(v, datetime.datetime):
                        setattr(self, k, v.strftime('%Y-%m-%d %H:%M:%S'))
                    elif isinstance(v, datetime.date):
                        setattr(self, k, v.strftime('%Y-%m-%d'))
                    else:
                        setattr(self, k, v)



class UserRole(User):
    def __init__(self, user_id):
        super(UserRole, self).__init__(user_id=user_id)
        self.master_role = ''
        self.slave_role_list = list()
        self.all_role_list = list()
        self.get_role()

    def get_role(self):
        try:
            self.master_role = UserAccount.objects.get(user_id=self.user_id).role_id
        except FieldError:
            self.master_role = UserAccount.objects.get(userid=self.user_id).role_id

        self.slave_role_list = list(UserRoleIdList.objects.filter(user_id=self.user_id).values_list('role_id', flat=True))
        self.all_role_list.extend(self.slave_role_list)
        self.all_role_list.append(self.master_role)
        self.all_role_list = list(set(self.all_role_list))


class UiInitData(UserRole, User):
    def __init__(self, user_id):
        super(UiInitData, self).__init__(user_id=user_id)

