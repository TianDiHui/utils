# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
|##desc: vmware操作类
|##:param: None
|##:return: None
|##@author： jhuang
|##@time：12/12/2017
|##参考文档：
https://www.cnblogs.com/berlin-sun/archive/2013/05/15/python_vm_command.html
在此这个基础上，增加：部分函数中文注解，克隆、设置备注、执行命令等功能

pysphere 官方文档：https://pypi.python.org/pypi/pysphere/
https://github.com/dannvix/pySphere/blob/master/pysphere/vi_server.py
"""
import ssl

import time

logger = logging.getLogger('django')
from utils.common_util import get_except

'''


Created on May 5, 2013

@author: Berlin
'''

from pysphere import VIServer, VIException, FaultTypes


# import esxi_exception
class ToolsStatus:
    # VMware Tools has never been installed or has not run in the virtual machine
    NOT_INSTALLED = 'NOT INSTALLED'

    # VMware Tools is not running.
    NOT_RUNNING = 'NOT RUNNING'

    # VMware Tools is running and the version is current.
    RUNNING = 'RUNNING'

    # VMware Tools is running, but the version is not current.
    RUNNING_OLD = 'RUNNING OLD'

    # Couldn't obtain the status of the VMwareTools.
    UNKNOWN = 'UNKNOWN'


# Server Control
class EsxiServer:
    server_ip = ''
    user_name = ''
    password = ''
    connect_flag = False
    server = None

    def opearte_guest_power(self, src_vm_name, operate):
        """"
       |##desc: 操作客户机电源（重启、关机、开机）,这种模式不需要vmtools,就是强制操作电源，不走操作系统 ，可能损坏数据
       |##:param: >vm1.power_on()
                        >vm1.reset()
                        >vm1.suspend() #since pysphere 0.1.5
                        >vm1.power_off()
       |##:return: None
       |##@author： jhuang
       |##@time：12/12/2017
       """
        ovm = self.server.get_vm_by_name(src_vm_name)

        if operate == 'power_on':
            ovm.power_on()
            return True
        elif operate == 'reset':
            ovm.reset()
            return True
        elif operate == 'suspend':
            ovm.suspend()
            return True
        elif operate == 'power_off':
            ovm.power_off()
            return True
        else:
            print "Operate guest error: operate can noly be set as power_on, reset, suspend, power_off"
            return False

    def clone(self, src_vm_name, dest_vm_name, datacenter=None, sync_run=True, folder=None, resourcepool=None,
              datastore=None, host=None, power_on=True, template=False,
              snapshot=None, linked=False):
        """
        |##desc: 克隆虚拟机
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：12/12/2017
        """
        # get_vm_by_name 在包含2个数据中心的情况下，需要指定参数  datacenter 其中的限定条件为datacenter
        # vm1 = server.get_vm_by_path("[DataStore1] Ubantu/Ubantu-10.vmx") 通过路径方法获取对象
        logger.debug(src_vm_name)
        logger.debug(datacenter)
        ovm = self.server.get_vm_by_name(src_vm_name, datacenter)
        new_vm = ovm.clone(dest_vm_name)

    def create_snapshot(self, src_vm_name, snapShotName):
        """
        |##desc: 创建快照
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：12/12/2017
        """
        ovm = self.server.get_vm_by_name(src_vm_name)
        ovm.create_snapshot(snapShotName)

    def set_ssl_no_verify(self):
        ssl._create_default_https_context = ssl._create_unverified_context

    # Use the given args to connect the esxi server you want
    # @ip[string]: ESXi server's IP address
    # @name[string]: the username used to login the ESXi server
    # @pwd[string]: the password used to login the ESXi server
    def connect_server(self, ip, name, pwd, ssl_no_verify=True):
        logger.debug(ip)
        logger.debug(name)
        logger.debug(pwd)
        self.server_ip = ip
        self.user_name = name
        self.password = pwd
        self.server = VIServer()
        if ssl_no_verify:
            self.set_ssl_no_verify()
        self.server.connect(self.server_ip, self.user_name, self.password)
        self.connect_flag = self.server.is_connected()
        if self.connect_flag:
            return True
        return False

    # To get all the definition registered vms from the connected server
    # @param[string]: can be set as ALL, POWER_ON, POWER_OFF, SUSPENDED
    # According to the param, returns a list of VM Paths. You might also filter by datacenter,
    # cluster, or resource pool by providing their name or MORs.
    # if  cluster is set, datacenter is ignored, and if resource pool is set
    # both, datacenter and cluster are ignored.
    def get_registered_vms(self, param='ALL', status=None, datacenter=None, cluster=None,
                           resource_pool=None):
        """
        获取注册的主机 （虚拟机）

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：28/02/2018
        """
        if param not in ['ALL', 'POWER_ON', 'POWER_OFF', 'SUSPENDED']:
            print "Get VMs error: param can only be set as ALL, POWER_ON, POWER_OFF, or SUSPENDED."
            return None
        if self.connect_flag == False:
            print "Get VMs error: Server not connected."
            return None
        if param == 'ALL':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool)
        elif param == 'POWER_ON':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool, status='poweredOn')
        elif param == 'POWER_OFF':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool, status='poweredOff')
        elif param == 'SUSPENDED':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool, status='suspended')
        else:
            return None

    # Disconnect to the Server
    def disconnect(self):
        if self.connect_flag is True:
            self.server = self.server.disconnect()
            self.connect_flag == False

    # To keep session alive
    def keep_session_alive(self):
        assert self.server.keep_session_alive()

    # To get the server type
    def get_server_type(self):
        return self.server.get_server_type()

    # To get performance manager
    def get_performance_manager(self):
        return self.server.get_performance_manager()

    # To get the all the server's hosts
    def get_all_hosts(self):
        """
        获取所有主机(这个是宿主机)
        Returns a dictionary of the existing hosts keys are their names
        and values their ManagedObjectReference object.
        """
        return self.server.get_hosts()

    # To get all datastores
    def get_all_datastores(self):
        """
        获取存储列表
        Returns a dictionary of the existing datastores. Keys are
        ManagedObjectReference and values datastore names.
        """
        return self.server.get_datastores()

    # To get all clusters
    def get_all_clusters(self):
        """
        获取所有集群列表
        Returns a dictionary of the existing clusters. Keys are their
        ManagedObjectReference objects and values their names.
        """
        return self.server.get_clusters()

    # To get all datacenters
    def get_all_datacenters(self):
        """
        获取数据中心列表
        Returns a dictionary of the existing datacenters. keys are their
        ManagedObjectReference objects and values their names.
        """
        return self.server.get_datacenters()

    # To get all resource pools
    def get_all_resource_pools(self):
        """
        Returns a dictionary of the existing ResourcePools. keys are their
        ManagedObjectReference objects and values their full path names.
        """
        return self.server.get_resource_pools()

    # To get hosts by name
    def get_hosts_by_name(self, from_mor):
        """
        Returns a dictionary of the existing ResourcePools. keys are their
        ManagedObjectReference objects and values their full path names.
        @from_mor: if given, retrieves the hosts contained within the specified
            managed entity.
        """
        try:
            hosts_dic = self.server.get_hosts(from_mor)
        except:
            print "Get hosts error!"
            return None
        return hosts_dic


# VMWare Control
class EsxiVmware:
    """任何除电源管理以外的操作都需要事先登录系统，这项操作需要vSphere 5.0以上，并且虚拟机必须安装vmware tools。
　　这项操作没有返回值，没有异常信息就是成功了。"""

    server_obj = None
    mac_address = ''
    path = ''
    guest_full_name = ''
    name = ''
    guest_id = ''
    vm = None
    guest_username = ''
    guest_password = ''
    status = ''
    snapshot_list = []
    __login_flag = False

    # Initialize vms, you can set the @parm[string] as VM path or VM name.
    # If you use VM path, set the @parm_type[string] as Path(Default),
    # If you use VM name, set the @parm_type[string] as Name
    # @esxi_server[EsxiServer]: the server where the vm in
    # @username[string]: the user name used to login vm system
    # @password[string]: the password used to login vm system
    def __init__(self, esxi_server, parm, username='', password='', parm_type='Name'):
        print parm, username, password, parm_type
        if parm_type in ['Path', 'Name']:
            self.server_obj = esxi_server
            self.__get_vmware(esxi_server, parm, parm_type)
            self.guest_username = username
            self.guest_password = password
        else:
            print "Get VMWare error: parm_type only can be set as 'Path' or 'Name'"

    # Private function
    # To get the vm you want
    def __get_vmware(self, esxi_server, parm, parm_type):
        if parm_type == 'Path':
            try:
                # self.vm = self.esxi_server.server.get_vm_by_path(parm)
                self.vm = esxi_server.server.get_vm_by_path(parm)
            except:
                print "Get VMWare error: Can not access the VM '" \
                      + parm + "'. Please check!"
                return
        elif parm_type == "Name":
            try:
                # self.vm = self.esxi_server.server.get_vm_by_name(parm)
                self.vm = esxi_server.server.get_vm_by_name(parm)
            except:
                print "Get VMWare error: Can not access the VM '" \
                      + parm + "'. Please check!"
                return

        self.mac_address = self.vm.get_property('mac_address')
        self.path = self.vm.get_property('path')
        self.guest_full_name = self.vm.get_property('guest_full_name')
        self.name = self.vm.get_property('name')
        self.guest_id = self.vm.get_property('guest_id')

    # To get the vm's status
    def get_status(self):
        self.status = self.vm.get_status()
        if self.status != 'POWERED ON':
            self.__login_flag = False

    # To get the vm's basic status: 'POWERED ON','POWERED OFF','SUSPENDED'
    def get_basic_status(self):
        self.status = self.vm.get_status(basic_status=True)
        if self.status != 'POWERED ON':
            self.__login_flag = False

    # To operate the VM
    """
    @operate[string]: can be set as POWER_ON, POWER_OFF, SUSPEND, RESET
    Return operate success or not
    @sync_run[bool]: means you operate the VM synchronously or not.
       True is synchronously
       False is asynchronously
    If sync_run set as False, status can not be None. status can be set as:
       queued, error, running, success
       return the task's status
    If @time_out[int] is 0 or negative, waits indefinitely"""

    def operate_vm(self, operate, sync_run=True, status=None, time_out=-1):
        if operate not in ['POWER_ON', 'POWER_OFF', 'SUSPEND', 'RESET']:
            print "Operate VM error: operate can only be set as POWER_ON, POWER_OFF, SUSPEND or RESET."
            return False
        if sync_run is True:
            return self.__operate_vm_syn(operate)

        elif sync_run == False:
            if status == None:
                print "Operate VM error: status can not be None while sync_run is True."
                return False
            if status not in ['queued', 'error', 'running', 'success']:
                print "Operate VM error: status can only be set as queued, error, running or success."
                return False
            if (time_out == -1) or (time_out == 0):
                print "Operate VM warning: time_out is 0 or negative, will waits indefinitely."
            return self.__operate_vm_asyn(operate, status, time_out)

    # Private function
    # To operate the VM synchronously
    def __operate_vm_syn(self, operate):
        if operate == "POWER_ON":
            self.get_status()
            if self.status in ['POWERED ON', 'POWERING ON']:
                print "Operate VM warning: VM named " + self.name + " is powered or powering on."
                return False
            self.vm.power_on()
            self.get_status()
            if self.vm.is_powering_on() or self.vm.is_powered_on():
                return True
            return False
        elif operate == "POWER_OFF":
            self.get_status()
            if self.status in ['POWERED OFF', 'POWERING OFF']:
                print "Operate VM warning: VM named " + self.name + " is powered or powering off."
                return False
            self.vm.power_off()
            self.get_status()
            if self.vm.is_powering_off() or self.vm.is_powered_off():
                return True
            return False
        elif operate == "SUSPEND":
            self.get_status()
            if self.status in ['SUSPENDED', 'SUSPENDING']:
                print "Operate VM warning: VM named " + self.name + " is suspended or suspending."
                return False
            self.vm.suspend()
            self.get_status()
            if self.vm.is_suspending() or self.vm.is_suspended():
                return True
            return False
        elif operate == "RESET":
            self.get_status()
            if self.status == 'RESETTING':
                print "Operate VM warning: VM named " + self.name + " is resetting."
                return False
            self.vm.reset()
            self.get_status()
            if self.vm.is_resetting():
                return True
            return False

    # Private function
    # To operate the VM asynchronously
    def __operate_vm_asyn(self, operate, status, time_out):
        if operate == "POWER_ON":
            self.get_status()
            if self.status in ['POWERED ON', 'POWERING ON']:
                print "Operate VM warning: VM named " + self.name + " is powered or powering on."
                return False
            task = self.vm.power_on(sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to power on the VM: ' + self.path \
                          + '. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for power on to finish"
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "POWER_OFF":
            self.get_status()
            if self.status in ['POWERED OFF', 'POWERING OFF']:
                print "Operate VM warning: VM named " + self.name + " is powered or powering off."
                return False
            task = self.vm.power_off(sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to power off the VM: ' + self.path \
                          + '. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for power off to finish"
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "SUSPEND":
            self.get_status()
            if self.status in ['SUSPENDED', 'SUSPENDING']:
                print "Operate VM warning: VM named " + self.name + " is suspended or suspending."
                return False
            task = self.vm.suspend(sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to suspend the VM: ' + self.path \
                          + '. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for suspend to finish"
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "RESET":
            self.get_status()
            if self.status == 'RESETTING':
                print "Operate VM warning: VM named " + self.name + " is resetting."
                return False
            task = self.vm.reset(sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to reset the VM: ' + self.path \
                          + '. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for reset to finish"
                return task.get_state()
            self.get_status()
            return task.get_state()

    # To get all the snapshots in the VM
    def get_all_snapshots(self):
        self.snapshot_list = self.vm.get_snapshots()

    # return all the snapshots' name in the VM
    def get_all_snapshots_name(self):
        names = []
        for snapshot in self.snapshot_list:
            names.append(snapshot.get_name())
        return names

    # To operate the snapshot
    """
    @operate[string]: can be set as REVERT_CURRENT, REVERT_NAMED, DELETE_CURRENT, DELETE_NAMED, CREATE
    If operate contains 'NAMED' or 'CREATE', @name[string] can not be None
    @sync_run[bool]: means you operate the VM synchronously or not.
       True is synchronously
       False is asynchronously
    If sync_run set as False, @status[string] can not be None. status can be set as:
       queued, error, running, success
    If @time_out[int] is 0 or negative, waits indefinitely
    @description[string] used when you create a snapshot"""

    def operate_snapshot(self, operate, name=None, description=None, sync_run=True, status=None, time_out=-1):
        if operate not in ['REVERT_CURRENT', 'REVERT_NAMED', 'DELETE_CURRENT', \
                           'DELETE_NAMED', 'CREATE']:
            print "Operate Snapshot error: operate can only be set as PREVERT_CURRENT, REVERT_NAMED, DELETE_CURRENT, DELETE_NAMED or CREATE."
            return False
        self.get_all_snapshots()
        if sync_run is True:
            return self.__operate_snapshot_syn(operate, name, description)

        elif sync_run == False:
            if status == None:
                print "Operate Snapshot error: status can not be None while sync_run is True."
                return False
            if status not in ['queued', 'error', 'running', 'success']:
                print "Operate Snapshot error: status can only be set as queued, error, running or success."
                return False
            if (time_out == -1) or (time_out == 0):
                print "Operate Snapshot warning: time_out is 0 or negative, will waits indefinitely."
            return self.__operate_snapshot_asyn(operate, name, status, time_out)

    # Private function
    # To operate the snapshot synchronously
    def __operate_snapshot_syn(self, operate, name, description):
        if operate == "REVERT_CURRENT":
            self.vm.revert_to_snapshot()
            self.get_status()
            return True
        elif operate == "REVERT_NAMED":
            if name is None:
                print "Operate Snapshot error: Please set snapshot name."
                return False
            names = self.get_all_snapshots_name()
            if name not in names:
                print "Operate Snapshot error: No snapshot named " \
                      + name + " in the VM named " + self.name + "."
                return False
            self.vm.revert_to_named_snapshot(name)
            self.get_status()
            return True
        elif operate == "DELETE_CURRENT":
            self.vm.delete_current_snapshot()
            self.get_status()
            return True
        elif operate == "DELETE_NAMED":
            if name is None:
                print "Operate Snapshot error: Please set snapshot name."
                return False
            names = self.get_all_snapshots_name()
            if name not in names:
                print "Operate Snapshot error: No snapshot named " \
                      + name + " in the VM named " + self.name + "."
                return False
            self.vm.delete_named_snapshot(name)
            self.get_status()
            return True
        elif operate == "CREATE":
            if name is None:
                print "Operate Snapshot error: Please set snapshot name."
                return False
            names = self.get_all_snapshots_name()
            if name in names:
                print "Operate Snapshot warning: Snapshot named " \
                      + name + " already in the VM named " + self.name + "."
            if (description is not None) and (description != ''):
                self.vm.create_snapshot(name, description)
            else:
                self.vm.create_snapshot(name)
            self.get_status()
            return True

    # Private function
    # To operate the snapshot asynchronously
    def __operate_snapshot_asyn(self, operate, name, status, time_out):
        if operate == "REVERT_CURRENT":
            task = self.vm.revert_to_snapshot(sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to revert to the current snapshot. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for revert to finish."
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "REVERT_NAMED":
            if name is None:
                print "Operate Snapshot error: Please set snapshot name."
                return False
            names = self.get_all_snapshots_name()
            if name not in names:
                print "Operate Snapshot error: No snapshot named " \
                      + name + " in the VM named " + self.name + "."
                return False
            task = self.vm.revert_to_named_snapshot(name, sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to revert to the current snapshot. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for revert to finish."
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "DELETE_CURRENT":
            task = self.vm.delete_current_snapshot(sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to revert to the current snapshot. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for revert to finish."
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "DELETE_NAMED":
            if name is None:
                print "Operate Snapshot error: Please set snapshot name."
                return False
            names = self.get_all_snapshots_name()
            if name not in names:
                print "Operate Snapshot error: No snapshot named " \
                      + name + " in the VM named " + self.name + "."
                return False
            task = self.vm.delete_named_snapshot(name, sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to revert to the current snapshot. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for revert to finish."
                return task.get_state()
            self.get_status()
            return task.get_state()
        elif operate == "CREATE":
            if name is None:
                print "Operate Snapshot error: Please set snapshot name."
                return False
            names = self.get_all_snapshots_name()
            if name in names:
                print "Operate Snapshot warning: Snapshot named " \
                      + name + " already in the VM named " + self.name + "."
            task = self.vm.create_snapshot(name, sync_run=False)
            try:
                status = task.wait_for_state([status, 'error'], timeout=time_out)
                if status == 'error':
                    print 'Failed to revert to the current snapshot. Error Message:', task.get_error_message()
            except:
                print str(time_out) + " seconds time out reached waiting for revert to finish."
                return task.get_state()
            self.get_status()
            return task.get_state()

    # To get VM's properties
    # @from_cache[bool]: True defualt will refresh the cache of all the properties, not only the requested.
    # return a list of the VM's properties
    def get_vm_properties(self, from_cache=True):
        if from_cache:
            return self.vm.get_properties()
        return self.vm.get_properties(from_cache=False)

    # To retrieve the value of the requested property, or None if that property does not exist.
    '''
    @properti_name[string]: the property name you request
    This is the list of all the properties you can request:
        name, path, guest_id, guest_full_name, hostname, ip_address, mac_address, net
    @from_cache[bool]: True defualt will refresh the cache of all the properties, not only the requested.
    return the name'''

    def get_vm_property(self, property_name, from_cache=True):
        if property_name not in ['name', 'path', 'guest_id', 'guest_full_name', 'hostname',
                                 'ip_address', 'mac_address', 'net', 'guest.toolsStatus']:
            print "Get VM property error: property_name must in one of 'name', 'path', 'guest_id', 'guest_full_name', 'hostname', 'ip_address', 'mac_address', 'net'"
            return None

        if from_cache:
            return self.vm.get_property(property_name)
        return self.vm.get_property(property_name, from_cache=False)

    # To get the name of the immediate resource pool the VM belongs to
    def get_resource_pool_name(self):
        return self.vm.get_resource_pool_name()

    def vm_login(self):
        """
        vmware tools 连接

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：01/03/2018
        """
        logger.debug(self.guest_username)
        logger.debug(self.guest_password)
        self.vm.login_in_guest(self.guest_username, self.guest_password)

    def send_file(self, local_path, guest_path, overwrite=True):
        """
        |##desc: 从本机的local_path发送一个文件到虚拟机的guest_path
        |##:param: cmd_args=[vm_ip,vm_netmask,vm_gateway,vm_main_dns]  cmd_path 脚本执行路径（远程服务器的）
        |##:return: None
        |##@author： jhuang
        |##@time：12/13/2017

        调用是实例：
        oESXi_Server=EsxiServer()
        oESXi_Server.connect_server('192.168.10.200','root','thzk211!')
        esxi_vmware= EsxiVmware(oESXi_Server,'Test1_1-emr-portal-slave 10.77','th','thzk211!')
        print esxi_vmware.send_file('d:/1.sh','/opt/earth/2.sh')
        """
        logger.debug(local_path)
        logger.debug(guest_path)
        self.vm.login_in_guest(self.guest_username, self.guest_password)
        pid = self.vm.send_file(local_path, guest_path, overwrite)

        return pid

    def start_porcess(self, cmd_path, cmd_args=None):
        """
        |##desc: 到虚拟机执行一个任务
        |##:param: cmd_args=[vm_ip,vm_netmask,vm_gateway,vm_main_dns]  cmd_path 脚本执行路径（远程服务器的）
        |##:return: None
        |##@author： jhuang
        |##@time：12/13/2017
        """
        self.vm.login_in_guest(self.guest_username, self.guest_password)
        logger.debug(self.guest_username)
        logger.debug(self.guest_password)
        logger.debug(cmd_path)
        logger.debug(cmd_args)
        pid = self.vm.start_process(cmd_path, args=cmd_args)

        return pid

    def operate_guest(self, operate):
        """
        # To login the VM
        #软重启、开关机器，需要操作系统用户名和密码、需要安装vmtools
        调用方法：
        oESXi_Server=EsxiServer()
        oESXi_Server.connect_server('192.168.10.200','root','thzk211!')
        esxi_vmware= EsxiVmware(oESXi_Server,'Test1_1-emr-portal-slave 10.77_clone')
        esxi_vmware.operate_guest('SHUTDOWN')


        # @operate[string]: can be set as LOGIN, SHUTDOWN, REBOOT, STANDBY
        # return operate success or not
        |##desc: None
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：12/13/2017
        """

        self.get_status()
        if self.status != 'POWERED ON':
            self.__login_flag = False
            print "Operate guest error: The VM " + self.name + " is not powered on."
            return False

        if operate not in ['LOGIN', 'SHUTDOWN', 'REBOOT', 'STANDBY']:
            print "Operate guest error: operate can noly be set as LOGIN, SHUTDOWN, REBOOT or STANDBY"
            return False
        if operate == 'LOGIN':
            # try:
            self.vm.login_in_guest(self.guest_username, self.guest_password)
            # except:
            #    print 'Operate guest error: login the VM named ' + self.name + ' failed. Please check the username and password.'
            #    return False
            self.__login_flag = True
            return True
        elif operate == 'SHUTDOWN':
            # try:
            self.vm.shutdown_guest()
            # except:
            #    print 'Operate guest error: Shut down the VM named ' + self.name + ' failed.'
            #    return False
            self.__login_flag = False
            return True
        elif operate == 'REBOOT':
            # try:
            self.vm.reboot_guest()
            # except:
            #    print 'Operate guest error: Reboot the VM named ' + self.name + ' failed.'
            #    return False
            self.__login_flag = False
            return True
        elif operate == 'STANDBY':
            # try:
            self.vm.standby_guest()
            # except:
            #    print 'Operate guest error: Stand by the VM named ' + self.name + ' failed.'
            #    return False
            self.__login_flag = False
            return True
        else:
            print "Operate guest error: Unknown operate."
            return False

    # To create directory in the VM
    # if @create_parents[bool] is True (default) all the directory components in the @path[string] are created if they don't exist.
    # return make directory succeed or not
    # warning: In order to use this function, you must login the VM first
    def make_directory(self, path, create_parents=True):
        if self.__login_flag == False:
            print 'Create directory error: Sorry, but please login the VM first.'
            return False
        # try:
        self.vm.make_directory(path, create_parents)
        # except:
        #    raise esxi_exception.MakeDirectoryException(path, self.name)
        return True

    # To move directory in the VM
    """
    @src_path[string]: the source path
    @dst_path[string]: the destination path
    return move directory succeed or not
    warning: In order to use this function, you must login the VM first"""

    def move_directory(self, src_path, dst_path):
        if self.__login_flag == False:
            print 'Move directory error: Sorry, but please login the VM first.'
            return False
        # try:
        self.vm.move_directory(src_path, dst_path)
        # except:
        #    raise esxi_exception.MoveDirectoryException(src_path, dst_path, self.name)
        return True

    # To delete directory in the VM
    # @path[string]: the directory you want to delete
    # If @recursive[bool] is True all subdirectories and files are also deleted, else the operation will fail if the directory is not empty.
    # return delete directory succeed or not
    # warning: In order to use this function, you must login the VM first
    def delete_directory(self, path, recursive):
        if self.__login_flag == False:
            print 'Delete directory error: Sorry, but please login the VM first.'
            return False
        # try:
        self.vm.delete_directory(path, recursive)
        # except:
        #    raise esxi_exception.DeleteDirectoryException(path, self.name)
        return True

    # To list all the files and directories of the path in the VM
    """
    @path[string]: is the complete path to the directory or file to query.
    Returns information about files or directories from the guest system.
    @match_pattern[perl-compatible regular expression]: is a filter for the return values specified
    as a perl-compatible regular expression (if not provided then '.' is used).
    The method returns a list of dictionaries with these keys:
       path: The complete path to the file
       size: The file size in bytes
       type: either 'directory', 'file', or 'symlink'
    warning: In order to use this function, you must login the VM first"""

    def list_files(self, path, match_pattern=None):
        if self.__login_flag == False:
            # print 'List files error: Sorry, but please login the VM first.'
            return None
            # try:
            #    file_list = self.vm.list_files(path, match_pattern)
            # except:
            # print "Can't get file from " + path + "."
        #    return None
        return self.vm.list_files(path, match_pattern)

    # To delete folders and files in the given path
    # @path[string]: the operation destination folder in the VM
    # return operate success of not
    def delete_files_in_folder(self, path):
        if self.delete_directory(path, True):
            if self.make_directory(path, create_parents=True):
                return True
        return False
