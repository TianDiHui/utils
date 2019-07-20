#!/usr/bin/env python
# -*- coding=utf-8 -*-


# http://blog.csdn.net/python_tty/article/details/73822071

import json
from collections import namedtuple

from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory, Host, Group
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars import VariableManager

# from SRMCenter.apps.global_var import  GlobalVar

logger = logging.getLogger('django')



from shell_util import exec_shell


def ssh_key_install(password, username, hostname):
    """
    |##desc: 安装ssh key
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/7/14
    """
    exec_shell("sshpass -p %s ssh-copy-id -i /root/.ssh/id_rsa.pub %s@%s" % (password, username, hostname), 5)



# 资产
class MyInventory(Inventory):
    def __init__(self, resource, loader, variable_manager):
        self.resource = resource
        self.inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=[])
        self.dynamic_inventory()

    def add_dynamic_group(self, hosts, groupname, groupvars=None):
        my_group = Group(name=groupname)
        if groupvars:
            for key, value in groupvars.iteritems():
                my_group.set_variable(key, value)
        for host in hosts:
            # set connection variables
            hostname = host.get("hostname")
            hostip = host.get('ip', hostname)
            hostport = host.get("port")
            username = host.get("username")
            password = host.get("password")
            ssh_key = host.get("ssh_key")
            my_host = Host(name=hostname, port=hostport)
            my_host.set_variable('ansible_ssh_host', hostip)
            my_host.set_variable('ansible_ssh_port', hostport)
            my_host.set_variable('ansible_ssh_user', username)
            my_host.set_variable('ansible_ssh_pass', password)
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)
            for key, value in host.iteritems():
                if key not in ["hostname", "port", "username", "password"]:
                    my_host.set_variable(key, value)
            my_group.add_host(my_host)

        self.inventory.add_group(my_group)

    def dynamic_inventory(self):
        if isinstance(self.resource, list):
            self.add_dynamic_group(self.resource, 'default_group')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.iteritems():
                self.add_dynamic_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("vars"))

class ModelResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result

# playbook运行结果
class PlayBookResultsCollector(CallbackBase):
    CALLBACK_VERSION = 2.0

    def __init__(self, taskList, *args, **kwargs):
        super(PlayBookResultsCollector, self).__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_skipped = {}
        self.task_failed = {}
        self.task_status = {}
        self.task_unreachable = {}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if taskList.has_key(result._host.get_name()):
            data = {}
            data['task'] = str(result._task).replace("TASK: ", "")
            taskList[result._host.get_name()].get('ok').append(data)
        self.task_ok[result._host.get_name()] = taskList[result._host.get_name()]['ok']

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if taskList.has_key(result._host.get_name()):
            data = {}
            data['task'] = str(result._task).replace("TASK: ", "")
            msg = result._result.get('stderr')
            if msg is None:
                results = result._result.get('results')
                if result:
                    task_item = {}
                    for rs in results:
                        msg = rs.get('msg')
                        if msg:
                            task_item[rs.get('item')] = msg
                            data['msg'] = task_item
                    taskList[result._host.get_name()]['failed'].append(data)
                else:
                    msg = result._result.get('msg')
                    data['msg'] = msg
                    taskList[result._host.get_name()].get('failed').append(data)
        else:
            data['msg'] = msg
            taskList[result._host.get_name()].get('failed').append(data)
        self.task_failed[result._host.get_name()] = taskList[result._host.get_name()]['failed']

    def v2_runner_on_unreachable(self, result):
        self.task_unreachable[result._host.get_name()] = result

    def v2_runner_on_skipped(self, result):
        if taskList.has_key(result._host.get_name()):
            data = {}
            data['task'] = str(result._task).replace("TASK: ", "")
            taskList[result._host.get_name()].get('skipped').append(data)
        self.task_ok[result._host.get_name()] = taskList[result._host.get_name()]['skipped']

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            self.task_status[h] = {
                "ok": t['ok'],
                "changed": t['changed'],
                "unreachable": t['unreachable'],
                "skipped": t['skipped'],
                "failed": t['failures']
            }

# 执行
class ANSRunner(object):
    def __init__(self, resource, *args, **kwargs):
        self.resource = resource
        self.inventory = None
        self.variable_manager = None
        self.loader = None
        self.options = None
        self.passwords = None
        self.callback = None
        self.__initializeData()
        self.results_raw = {}

    def __initializeData(self):
        # ansible_ssh_host：指定主机别名对应的真实IP，如：251 ansible_ssh_host=192.168.116.251，随后连接该主机无须指定完整IP，只需指定251 就行
        # ansible_ssh_port：指定连接到这个主机的ssh 端口，默认22
        # ansible_ssh_user：连接到该主机的ssh用户
        # ansible_ssh_pass：连接到该主机的ssh密码（连-k 选项都省了），安全考虑还是建议使用私钥或在命令行指定-k 选项输入
        # ansible_sudo_pass：sudo 密码
        # ansible_sudo_exe(v1.8+的新特性):sudo 命令路径
        # ansible_connection：连接类型，可以是local、ssh 或paramiko，ansible1.2 之前默认为paramiko
        # ansible_ssh_private_key_file：私钥文件路径
        # ansible_shell_type：目标系统的shell类型，默认为sh,如果设置csh/fish，那么命令需要遵循它们语法
        # ansible_python_interpreter：python 解释器路径，默认是/usr/bin/python，但是如要要连freeBSD系统的话，就需要该指令修改python路径
        # ansible_*_interpreter：这里的"*"可以是ruby或perl或其他语言的解释器，作用和ansible_python_interpreter类似


        Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'timeout', 'remote_user',
                                         'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                         'sftp_extra_args',
                                         'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass',
                                         'verbosity',
                                         'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])

        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        # "http://www.cnblogs.com/sanyuanempire/p/6169489.html"
        # self.options = Options(connection='smart', module_path=None, forks=10, timeout=10,
        #                        remote_user='root', ask_pass=False, private_key_file=None,
        #                        ssh_common_args='-o StrictHostKeyChecking=no', ssh_extra_args=None,
        #                        sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,
        #                        become_user='root', ask_value_pass=False, verbosity=None, check=False, listhosts=False,
        #                        listtasks=False, listtags=False, syntax=False)

        self.options = Options(connection='smart', module_path='/usr/share/ansible', forks=100, timeout=10,
                               remote_user='root', ask_pass=False, private_key_file=None, ssh_common_args=None,
                               ssh_extra_args=None,
                               sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,
                               become_user='root', ask_value_pass=False, verbosity=None, check=False, listhosts=False,
                               listtasks=False, listtags=False, syntax=False)

        self.passwords = dict(sshpass=None, becomepass=None)
        self.inventory = MyInventory(self.resource, self.loader, self.variable_manager).inventory
        self.variable_manager.set_inventory(self.inventory)

    def run_model(self, host_list, module_name, module_args):
        """
        run module from andible ad-hoc.
        module_name: ansible module_name
        module_args: ansible module args
        """
        play_source = dict(
            name="Ansible Play",
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        self.callback = ModelResultsCollector()
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
            )
            tqm._stdout_callback = self.callback
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def run_playbook(self, host_list, playbook_path, ):
        """
        run ansible palybook
        """
        global taskList
        taskList = {}
        for host in host_list:
            taskList[host] = {}
            taskList[host]['ok'] = []
            taskList[host]['failed'] = []
            taskList[host]['skppied'] = []
        try:
            self.callback = PlayBookResultsCollector(taskList)
            executor = PlaybookExecutor(
                playbooks=[playbook_path], inventory=self.inventory, variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options, passwords=self.passwords,
            )
            executor._tqm._stdout_callback = self.callback
            executor.run()
        except Exception as e:
            print e
            return False

    def get_model_result(self):
        self.results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_ok.items():
            self.results_raw['success'][host] = result._result

        for host, result in self.callback.host_failed.items():
            self.results_raw['failed'][host] = result._result

        for host, result in self.callback.host_unreachable.items():
            self.results_raw['unreachable'][host] = result._result
        return json.dumps(self.results_raw)

    def get_playbook_result(self):
        self.results_raw = {'skipped': {}, 'failed': {}, 'ok': {}, "status": {}, 'unreachable': {}}

        for host, result in self.callback.task_ok.items():
            self.results_raw['ok'][host] = result

        for host, result in self.callback.task_failed.items():
            self.results_raw['failed'][host] = result


# interface
# ----------------------------------------------------------
# def ssh_pass_multi(hostInfo_list):
#     """
#     |##desc: 批量安装ssh key
#     |##:param: None
#     |##:return: None
#     |##@author： jhuang
#     |##@time：2017/7/14
#     """
#     logger.debug('安装SSH公钥...')
#     ansibleList = []
#     for r in hostInfo_list:
#         dic = {}
#         dic['hostname'] = r['hostname']
#         dic['username'] = r['username']
#         dic['password'] = r['password']
#         ansibleList.append((None, dic))
#     GlobalVar.ansible_thread_pool.start(ssh_key_install, ansibleList)


def ansible_copy(hostInfo_list, src, dest, module_name='copy', toJson=True):
    """
    |##desc: ansible远程复制
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/7/14
    """

    # hostInfo_list = sql_to_list('''select t.server_ip as hostname,t.server_port as port, t.oracle_user as username,t.oracle_pwd as password
    #                              from server_instance t
    #                              where t.server_id in ('%s')''' % (server_id_list_checking), None, True)
    # 常用module_name :
    # command  执行简单命令
    # copy  复制文件
    # shell 执行脚本内容
    module_name = str(module_name).lower()
    module_args = "src=%s  dest=%s" % (src, dest)
    oANS = ANSRunner(hostInfo_list)
    logger.debug(hostInfo_list)
    host_list = []
    logger.debug(hostInfo_list)
    for r in hostInfo_list:
        host_list.append(r['hostname'])
    logger.debug(host_list)

    logger.debug('module_args:' + module_args)
    oANS.run_model(host_list=host_list, module_name=module_name, module_args=module_args)
    data = oANS.get_model_result()
    if toJson:
        data = json.loads(data)
    return data


def ansible_script(hostInfo_list, module_args, module_name='script', toJson=True):
    """
    |##desc: 执行ansible指令
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017/7/14
    """

    # hostInfo_list = sql_to_list('''select t.server_ip as hostname,t.server_port as port, t.oracle_user as username,t.oracle_pwd as password
    #                              from server_instance t
    #                              where t.server_id in ('%s')''' % (server_id_list_checking), None, True)
    # 常用module_name :
    # command  执行简单命令
    # copy  复制文件
    # shell 执行脚本内容
    module_name = str(module_name).lower()

    oANS = ANSRunner(hostInfo_list)
    logger.debug(hostInfo_list)
    host_list = []
    logger.debug(hostInfo_list)
    for r in hostInfo_list:
        host_list.append(r['hostname'])
    logger.debug(host_list)

    logger.debug('module_args:' + module_args)
    oANS.run_model(host_list=host_list, module_name=module_name, module_args=module_args)
    data = oANS.get_model_result()
    if toJson:
        data = json.loads(data)
    return data
