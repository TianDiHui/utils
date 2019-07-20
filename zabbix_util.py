# -*- coding: utf-8 -*-
'''
@author: lanxiong lanxiong@cenboomh.com
@file: zabbix_util.py
@time: 2018/8/6 16:10
@desc:
'''
import json

import requests
from pyzabbix import ZabbixAPI

from SRMCenter.utils.common_util import get_except


class ZabbixWeb(object):
    """
    zabbix web api
    参考：https://blog.csdn.net/python_tty/article/details/53535669
    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：9/29/2018
    """

    def __init__(self, zabbix_url, zabbix_user, zabbix_password):
        self.zabbix_url = zabbix_url
        self.zabbix_user = zabbix_user
        self.zabbix_password = zabbix_password
        self.toekn_id = ''

    def get_login_session(self):
        data = json.dumps(
            {"jsonrpc": "2.0", "method": "user.login",
             "params": {"user": self.zabbix_user, "password": self.zabbix_password, }, "id": 3})
        header = {"Content-Type": "application/json"}
        try:
            req = requests.post("{zabbix_url}api_jsonrpc.php".format(zabbix_url=self.zabbix_url), headers=header,
                                data=data)
        except Exception, exc:
            raise
        else:
            rest = req.json()
            self.toekn_id = rest.get("result")
        return self.toekn_id


class ZabbixUtil(object):
    def __init__(self, api, user, pwd):
        self.api = api
        self.user = user
        self.pwd = pwd
        self.zbx = None
        self.__initializeData()

    def __initializeData(self):
        try:
            self.zbx = ZabbixAPI(self.api, timeout=4)
            self.zbx.login(self.user, self.pwd)
        except Exception as e:
            get_except(e)
            raise Exception("初始化zabbix失败，可能连不上zabbix api, 您可以选择跳过。 ")

    def query_hostinterface_by_ip(self, ip):
        hostinterface = self.zbx.hostinterface.get(filter={"ip": ip})
        return hostinterface

    def query_hostgroup_by_hostid(self, hostid):
        groups = self.zbx.host.get(selectGroups="extend", output=["hostid"], filter={"hostid": hostid})
        return groups


class ZabbixMaintenance(ZabbixUtil):
    def __init__(self, **zabbix_service_info):

        super(ZabbixMaintenance, self).__init__(zabbix_service_info["zabbix_service_api"],
                                                zabbix_service_info["zabbix_admin_user"],
                                                zabbix_service_info["zabbix_admin_pwd"]
                                                )

    def create_maintenance(self, **maintenance_dict):
        self.hostid_list = list()
        if 'hostid_list' in maintenance_dict:
            self.hostid_list = maintenance_dict['hostid_list']
        else:
            for host in maintenance_dict['maintenance_host_list']:
                hostinterface_list = self.query_hostinterface_by_ip(host)
                if hostinterface_list:
                    for host in hostinterface_list:
                        self.hostid_list.append(int(host['hostid']))

        self.hostid_list = list(set(self.hostid_list))
        self.maintenance_name = maintenance_dict['name']
        self.maintenance_active_since = maintenance_dict['maintenance_active_since']
        self.maintenance_active_till = maintenance_dict['maintenance_active_till']
        self.start_date = self.maintenance_active_since
        self.period = self.maintenance_active_till - self.maintenance_active_since

        maintenance = self.zbx.maintenance.create(name=self.maintenance_name,
                                                  hostids=self.hostid_list,
                                                  active_since=self.maintenance_active_since,
                                                  active_till=self.maintenance_active_till,
                                                  timeperiods=[{"start_date": self.start_date, "period": self.period}]
                                                  )
        return maintenance

    def update_maintenance(self, **maintenance_dict):
        self.hostid_list = list()
        if 'hostid_list' in maintenance_dict:
            self.hostid_list = maintenance_dict['hostid_list']
        else:
            for host in maintenance_dict['maintenance_host_list']:
                hostinterface_list = self.query_hostinterface_by_ip(host)
                if hostinterface_list:
                    for host in hostinterface_list:
                        self.hostid_list.append(int(host['hostid']))

        self.hostid_list = list(set(self.hostid_list))
        self.maintenance_name = maintenance_dict['name']
        self.maintenance_active_since = maintenance_dict['maintenance_active_since']
        self.maintenance_active_till = maintenance_dict['maintenance_active_till']
        self.start_date = self.maintenance_active_since
        self.period = self.maintenance_active_till - self.maintenance_active_since
        maintenance = self.get_maintenance_by_name(self.maintenance_name)
        maintenanceid = maintenance[0]['maintenanceid']
        maintenance = self.zbx.maintenance.update(maintenanceid=maintenanceid,
                                                  hostids=self.hostid_list,
                                                  active_since=self.maintenance_active_since,
                                                  active_till=self.maintenance_active_till,
                                                  timeperiods=[{"start_date": self.start_date, "period": self.period}]
                                                  )
        return maintenance

    def get_maintenance_by_name(self, name):
        maintenance = self.zbx.maintenance.get(filter={"name": name})
        return maintenance

    def delete_maintenance_by_id(self, id):
        maintenance = self.zbx.maintenance.delete(id)
        return maintenance

    def delete_maintenance_by_name(self, name):
        zbx_main_list = self.get_maintenance_by_name(name)
        if zbx_main_list:
            for i in zbx_main_list:
                maintenanceid = i['maintenanceid']
                self.delete_maintenance_by_id(maintenanceid)


if __name__ == "__main__":
    host_list = [u'10.1.200.53', u'10.1.200.27', u'10.1.200.26', u'10.1.200.25', u'10.1.200.24', u'10.1.200.23',
                 u'10.1.200.22', u'10.1.200.21', u'10.1.200.20', u'10.1.200.45', u'10.1.200.44', u'10.1.200.47',
                 u'10.1.200.46', u'10.1.200.41', u'10.1.200.40', u'10.1.200.29', u'10.1.200.28', u'10.1.200.43',
                 u'10.1.200.42', u'10.1.200.18', u'10.1.200.19', u'10.1.200.17', u'10.1.200.34', u'10.1.200.35',
                 u'10.1.200.36', u'10.1.200.37', u'10.1.200.30', u'10.1.200.31', u'10.1.200.32', u'10.1.200.33',
                 u'10.1.200.38', u'10.1.200.39', u'10.1.200.52', u'10.1.200.50', u'10.1.200.51', u'10.1.200.49',
                 u'10.1.200.48', u'10.1.200.54', u'10.1.200.16', u'10.1.210.6', u'10.1.200.59', u'10.1.200.88',
                 u'10.3.255.81']
    maintenance_dict = {
        "name": "test_main",
        # "maintenance_host_list": [u'192.18.101.66', u'192.168.20.2'],
        "maintenance_host_list": host_list,
        "maintenance_active_since": 1533612598,
        "maintenance_active_till": 1533615598
    }

    # print ZabbixMaintenance("http://monitor.cenboomh.com", 'admin', 'thzk211!', **maintenance_dict).create_maintenance()
    # print zm.create_maintenance()
    zbx_main = ZabbixMaintenance("http://monitor.cenboomh.com", 'admin', 'thzk211!')
    print zbx_main.delete_maintenance_by_name("LZSFY")
    # print zbx_main.delete_maintenance_by_id(14)
