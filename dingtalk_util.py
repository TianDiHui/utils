# -*- coding: utf-8 -*-
'''
@author: lanxiong lanxiong@cenboomh.com
@file: dingtalk_util.py
@time: 2018/8/14 21:38
@desc:
'''

import json
import time

from django.core.exceptions import ObjectDoesNotExist
from retrying import retry
from ..models.models import SysParam
from http_util import HttpClass
logger = logging.getLogger('django')


logger = Logger("dingtalk").init()

Dingtalk_API = "https://oapi.dingtalk.com"


class Dingtalk(object):
    def __init__(self, corpid, corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.access_token = ''
        self.http_obj = HttpClass(headers={"Content-Type": "application/json"})
        self.__gettoken()

    def get_data_by_get(self, api):
        try:
            res, res_text, res_time = self.http_obj.get(api)
            res_dict = json.loads(res_text)
            if res_dict['errcode'] == 0:
                return res_dict
            else:
                raise Exception('errcode: ' + str(res_dict['errcode']) + res_dict['errmsg'].encode('utf8'))
        except Exception as e:
            logger.error(e)
            raise
            # logger.error("请求dingding API返回: " + e.message)
            # raise Exception("请求dingding API返回: " + e.message)

    def get_data_by_post(self, api, payload):
        try:
            res, res_text = self.http_obj.post(api, payload)
            res_dict = json.loads(res_text)
            if res_dict['errcode'] == 0:
                return res_dict
            else:
                raise Exception('errcode: ' + str(res_dict['errcode']) + res_dict['errmsg'].encode('utf8'))
        except Exception as e:
            logger.error(e)
            raise
            # logger.error("请求dingding API返回: " + e.message)
            # raise Exception("请求dingding API返回: " + e.message)

    @retry(stop_max_attempt_number=20, wait_fixed=8000)
    def __gettoken(self):
        # api https://oapi.dingtalk.com/gettoken?corpid=id&corpsecret=secrect
        # 检查mysql 连接是否可用
        try:
            from django.db import connections
            for conn in connections.all():
                conn.close_if_unusable_or_obsolete()
        except Exception as e:
            logger.error('关闭无效数据库连接失败 %s conn.close_if_unusable_or_obsolete()' % e)

        try:
            logger.info('从数据库获取dingtalk_token_info')
            obj_sysparam = SysParam.objects.get(param_name='dingtalk_token_info')
            dingtalk_token_info = obj_sysparam.param_value
        except ObjectDoesNotExist as e:
            dingtalk_token_info = None
        except Exception as e:
            logger.error(e)
            raise

        def __set_token():
            api = """{}/gettoken?corpid={}&corpsecret={}""".format(Dingtalk_API, self.corpid, self.corpsecret)
            res_dict = self.get_data_by_get(api)
            self.access_token = res_dict['access_token']
            dingtalk_token_info = "%s|%s|%s" % (time.time(), res_dict['expires_in'], res_dict['access_token'])
            obj_sysparam = SysParam.objects.get(param_name='dingtalk_token_info')
            obj_sysparam.param_value = dingtalk_token_info
            obj_sysparam.save()
            logger.info('dingtalk_token_info %s，获取dingtalk token' % dingtalk_token_info)

        if dingtalk_token_info is None:
            logger.info('dingtalk_token_info not exists, 重新设置token')
            __set_token()
        else:
            get_time = float(dingtalk_token_info.split('|')[0])
            expires_in = float(dingtalk_token_info.split('|')[1])
            access_token = str(dingtalk_token_info.split('|')[2])
            now_time = time.time()
            if now_time - get_time >= expires_in:
                logger.info('dingtalk_token_info %s已经过期，重新获取' % dingtalk_token_info)
                __set_token()
            else:
                self.access_token = access_token

    def get_all_department(self, only_get_id=True):
        """
        获取部门列表（非详情）
        @author： lanxiong
        @time：2018/8/15
        """
        dpt_list = list()
        api = """{}/department/list?access_token={}""".format(Dingtalk_API, self.access_token)
        res_dict = self.get_data_by_get(api)
        if only_get_id is True:
            for dpt in res_dict['department']:
                dpt_list.append(dpt['id'])
            return dpt_list
        else:
            return res_dict['department']

    def get_department_member_userids_list_by_dptid(self, department_id):
        """
        获取部门用户userid列表
        @author： lanxiong
        @time：2018/8/15
        """
        # https: //oapi.dingtalk.com/user/getDeptMember?access_token = ACCESS_TOKEN & deptId = 1
        api = """{}/user/getDeptMember?access_token={}&deptId={}""".format(Dingtalk_API, self.access_token,
                                                                           department_id)
        res_dict = self.get_data_by_get(api)
        return res_dict['userIds']

    def get_all_member(self, only_get_id=True):
        """
        获取所有员工
        @author： lanxiong
        @time：2018/8/16
        """
        all_user = list()
        all_user_id = list()
        dptid_list = self.get_all_department(only_get_id=True)

        for dptid in dptid_list:
            dept_users_list = self.get_department_member_userids_list_by_dptid(dptid)
            for i in dept_users_list:
                all_user_id.append(i)

        if only_get_id is True:
            return all_user_id
        else:
            for id in all_user_id:
                user = self.get_user_detail_by_userid(id)
                all_user.append(user)
            return all_user

    def get_user_detail_by_userid(self, userid):
        """
        获取员工详情
        @author： lanxiong
        @time：2018/8/15
        """
        api = """{}/user/get?access_token={}&userid={}""".format(Dingtalk_API, self.access_token, userid)
        res_dict = self.get_data_by_get(api)
        return res_dict

    def get_attendance_by_departmentid(self, department_id, checkDateFrom, checkDateTo):
        """
        获取部门考勤详细信息
        https://oapi.dingtalk.com/attendance/listRecord?access_token=ACCESS_TOKEN
        @author： lanxiong
        @time：2018/8/15
        """
        pass

    def get_attendance_by_userids_list(self, userids_list, checkDateFrom, checkDateTo):
        """
        获取员工详细考勤信息
        {
            "userIds": ["001","002"],
            "checkDateFrom": "yyyy-MM-dd hh:mm:ss",
            "checkDateTo": "yyyy-MM-dd hh:mm:ss",
            "isI18n":"false"
        }
        @author： lanxiong
        @time：2018/8/15
        """
        api = """{}/attendance/listRecord?access_token={}""".format(Dingtalk_API, self.access_token)
        payload = {
            "userIds": userids_list,
            "checkDateFrom": str(checkDateFrom),
            "checkDateTo": str(checkDateTo),
            "isI18n": "false"
        }
        res_dict = self.get_data_by_post(api, json.dumps(payload))
        return res_dict

    def get_attendance_by_userid(self, userid, checkDateFrom, checkDateTo):
        """
        获取员工详细考勤信息
        {
            "userIds": ["001"],
            "checkDateFrom": "yyyy-MM-dd hh:mm:ss",
            "checkDateTo": "yyyy-MM-dd hh:mm:ss",
            "isI18n":"false"
        }
        @author： lanxiong
        @time：2018/8/15
        """
        api = """{}/attendance/listRecord?access_token={}""".format(Dingtalk_API, self.access_token)
        payload = {
            "userIds": [userid],
            "checkDateFrom": str(checkDateFrom),
            "checkDateTo": str(checkDateTo),
            "isI18n": "false"
        }
        res_dict = self.get_data_by_post(api, json.dumps(payload))
        return res_dict

    def get_processinstance_by_id(self, process_instance_id):
        """
        获取单个审批实例
        Doc: https://open-doc.dingtalk.com/microapp/serverapi2/xgqkvx
        API: https://oapi.dingtalk.com/topapi/processinstance/get?access_token=ACCESS_TOKEN
        @author： lanxiong
        @time：2018/8/16
        """
        api = """{}/topapi/processinstance/get?access_token={}""".format(Dingtalk_API,
                                                                         self.access_token)
        payload = {
            "process_instance_id": process_instance_id
        }
        logger.info(self.access_token)
        res_dict = self.get_data_by_post(api, json.dumps(payload))
        return res_dict

    def get_processinstance_list(self, process_code, start_time, **kwargs):
        """
        批量获取审批实例
        Doc: https://open-doc.dingtalk.com/microapp/serverapi2/fpn98d
        API: https://oapi.dingtalk.com/topapi/processinstance/list?access_token=ACCESS_TOKEN
        process_code: 流程模板唯一标识
        start_time: 时间戳毫秒
        @author： lanxiong
        @time：2018/8/16
        """
        api = """{}/topapi/processinstance/list?access_token={}""".format(Dingtalk_API,
                                                                          self.access_token)
        payload = {
            "process_code": process_code,
            "start_time": start_time,
            "cursor": 0
        }
        payload.update(kwargs)
        processinstance_list = list()
        while True:
            res_dict = self.get_data_by_post(api, json.dumps(payload))
            if res_dict['result']['list']:
                processinstance_list.extend(res_dict['result']['list'])
            if 'next_cursor' in res_dict['result']:
                payload['cursor'] += 1
            else:
                break
        return processinstance_list

    def get_processinstance_list_all(self, start_time, **kwargs):
        """
        获取所有审批实例
        start_time 必填
        默认获取从指定日期到当前
        @author： lanxiong
        @time：2018/8/18
        """
        processinstance_all_list = list()
        for process_code in self.get_process_code_list():
            processinstance_list = self.get_processinstance_list(process_code, start_time, **kwargs)
            if processinstance_list:
                processinstance_all_list.append(processinstance_list)
        return processinstance_all_list

    def get_process_list(self, offset=0, size=100):
        """
        获取用户可见的审批模板
        https://open-doc.dingtalk.com/microapp/serverapi2/fpn98d
        API: https://oapi.dingtalk.com/topapi/process/listbyuserid?access_token=ACCESS_TOKEN
        @author： lanxiong
        @time：2018/8/16
        """
        # https://oapi.dingtalk.com/topapi/process/listbyuserid?access_token=ACCESS_TOKEN
        api = """{}/topapi/process/listbyuserid?access_token={}""".format(Dingtalk_API,
                                                                          self.access_token)
        process_list = list()
        payload = {
            "offset": offset,
            "size": size
        }
        while True:
            res_dict = self.get_data_by_post(api, json.dumps(payload))
            for proc in res_dict['result']['process_list']:
                process_list.append(proc)
            if 'next_cursor' in res_dict['result']:
                offset += 1
            else:
                break

        return process_list

    def get_process_code_list(self, proc_name_like=''):
        """
        获取用户可见的审批模板id
        @author： lanxiong
        @time：2018/8/16
        """
        process_code_list = list()
        for proc in self.get_process_list():
            process_code_list.append(proc['process_code'])
        return process_code_list

    def get_leave_approve_duration(self, userid, from_date, to_date):
        """
        获取请假时长 分钟
        Doc: https://open-doc.dingtalk.com/microapp/serverapi2/bdz3a3
        API: https://oapi.dingtalk.com/topapi/attendance/getleaveapproveduration?access_token=ACCESS_TOKEN
        @author： lanxiong
        @time：2018/8/17
        """
        api = """{}/topapi/attendance/getleaveapproveduration?access_token={}""".format(Dingtalk_API,
                                                                                        self.access_token)
        payload = {
            "userid": userid,
            "from_date": from_date,
            "to_date": to_date
        }
        res_dict = self.get_data_by_post(api, json.dumps(payload))
        duration_in_minutes = res_dict['result']['duration_in_minutes']
        return duration_in_minutes

    def get_attendance_getsimplegroups(self, **payload):
        """
        获取考勤组详情
        Doc: https://open-doc.dingtalk.com/microapp/serverapi2/tc6f5p
        API: https://oapi.dingtalk.com/topapi/attendance/getsimplegroups?access_token=ACCESS_TOKEN
        @author： lanxiong
        @time：2018/8/20
        """
        api = """{}/topapi/attendance/getsimplegroups?access_token={}""".format(Dingtalk_API,
                                                                                self.access_token)
        res_dict = self.get_data_by_post(api, json.dumps(payload))
        return res_dict

    def get_no_attendance(self, userid, start_time, end_time):
        process_list = self.get_process_list()

    def get_checkin_by_dpt_id(self, department_id, start_time, end_time):
        """
        获取签到
        Doc: https://open-doc.dingtalk.com/microapp/serverapi2/xmfmlh
        API: https://oapi.dingtalk.com/checkin/record?access_token=ACCESS_TOKEN&department_id=1&start_time=1467707227000&end_time=1467707240000&offset=0&size=100&order=asc
        start_time 开始时间。Unix时间戳，如：1520956800000
        """
        api = """{Dingtalk_API}/checkin/record?access_token={access_token}&department_id={department_id}&start_time={start_time:}&end_time={end_time}""".format(
            Dingtalk_API=Dingtalk_API,
            access_token=self.access_token,
            department_id=department_id,
            start_time=start_time,
            end_time=end_time
        )
        res_dict = self.get_data_by_get(api)
        return res_dict['data']
