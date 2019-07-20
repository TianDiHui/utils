# -*- coding: utf-8 -*-
"""
| ##@函数目的: SSH 和SFTP 连接类
| ##@参数说明： 
| ##@返回值：
| ##@函数逻辑：
| ##@开发人：jhuang
| ##@时间：
"""

import os
import re
import time

import paramiko

from SRMCenter.apps.global_var import GlobalVar
from file_util import get_file_size, file_path_parse
logger = logging.getLogger('django')
from string_util import covert_bytes, get_uuid


def ssh_pwd_decrypt(function):
    """
        装饰器，SSH 密码 解密

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: 返回json格式的异常到前台
        :raises keyError: raises an exception
        @author： jhuang
        @time：08/02/2018
    """

    def wrapper(*args, **kwargs):
        list_args = list(args)
        try:
            if len(list_args) > 4:
                re_pwd = re.findall('\^_\^(.*?)\^_\^', list_args[4])
                if len(re_pwd) == 1:
                    logger.debug('SSH密码被加密，需要解密...')
                    list_args[4] = GlobalVar.string_crypt.decrypt(re_pwd[0])
                    list_args = tuple(list_args)
                    return function(*list_args, **kwargs)

            if kwargs.has_key('pwd'):
                re_pwd = re.findall('\^_\^(.*?)\^_\^', kwargs['pwd'])
                if len(re_pwd) == 1:
                    logger.debug('SSH密码被加密，需要解密...')
                    kwargs['pwd'] = GlobalVar.string_crypt.decrypt(re_pwd[0])
                    return function(*args, **kwargs)

            print (args, kwargs)
            return function(*args, **kwargs)
        except Exception as e:
            # logger.debug('SSH密码被加密，需要解密...')
            logger.exception('ssh_pwd_decrypt')
            raise

    return wrapper


def ssh_command_multi(hostInfo_list, local_file):
    """
    | ##@函数目的: 批量执行指令
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    hostInfp_list_new = []
    # 事务ID
    transacton_id = get_uuid()

    for r in hostInfo_list:
        dic = {}
        dic['ip'] = r['ip']
        dic['port'] = r['port']
        dic['user'] = r['user']
        dic['pwd'] = r['pwd']
        dic['local_file'] = local_file
        dic['nohup'] = False
        dic['transacton_id'] = transacton_id
        hostInfp_list_new.append((None, dic))

    # GlobalVar.ssh_thread_pool.start(sshLocalScript, hostInfp_list_new)
    return transacton_id


def scp_put_multi(hostInfo_list, local_file, remote_file):
    """
    | ##@函数目的: 批量上传文件
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    # 事务ID
    transacton_id = get_uuid()
    hostInfp_list_new = []
    for r in hostInfo_list:
        dic = {}
        dic['ip'] = r['ip']
        dic['port'] = r['port']
        dic['user'] = r['user']
        dic['pwd'] = r['pwd']
        dic['local_file'] = local_file
        dic['remote_file'] = remote_file
        dic['transacton_id'] = transacton_id
        hostInfp_list_new.append((None, dic))

    GlobalVar.ssh_thread_pool.start(scp_put, hostInfp_list_new)


def ssh_command(ip, port, user, pwd, cmd, log=True):
    """
    | ##@函数目的: 执行一个远程linxu命令
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    ssh = ClassSSH()
    ssh.open(ip, port, user, pwd)
    ret = ssh.execute(cmd, log)
    ssh.close()
    return ret


def scp_get(ip, port, user, pwd, remote_file, local_file):
    """
    | ##@函数目的: 下载文件
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    scp = ClassSCP()
    scp.open(ip, port, user, pwd)
    scp.download_file(remote_file, local_file)
    scp.close()


def scp_put(ip, port, user, pwd, local_file, remote_file, transacton_id=''):
    """
    | ##@函数目的: 上传文件
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    scp = ClassSCP()
    scp.open(ip, port, user, pwd)
    scp.upload_file(local_file, remote_file)

    scp.close()


class ClassSSH():
    '''
    SSH类
    '''

    def __init__(self):
        self.ip = None
        self.port = None
        self.user = None
        self.pwd = None
        self.timeout = None
        self.env = None

    def exec_local_script(self, local_file, remote_file=None, param='', nohup=False, execute_by_channel=False):
        """
        | ##@函数目的: 调用本地脚本到远程执行
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        if remote_file is None:
            remote_file = '/tmp/%s' % (file_path_parse(local_file, 2))
        # logger.debug(local_file)
        extension = str(file_path_parse(local_file, 0)).lower()
        if extension == 'py':
            sheller = 'python'
        else:
            sheller = 'sh'
        scp_put(self.ip, self.port, self.user, self.pwd, local_file, remote_file)
        if nohup:
            cmd = 'nohup %s %s %s > /dev/null 2>&1 &' % (sheller, remote_file, param)
        else:
            cmd = '%s %s %s' % (sheller, remote_file, param)
        if execute_by_channel:
            exit_code, res = self.execute_by_channel(cmd)
            logger.debug("%s %s" % (exit_code, res))
            return exit_code, res
        else:
            ret = self.execute(cmd)
            logger.debug(ret)

        # self.execute('rm -f %s' % (remote_file))

        return ret

    @ssh_pwd_decrypt
    def open(self, ip, port, user, pwd, timeout=10, env=None):
        '''
        打开ssh
        '''
        ip = str(ip).strip()
        port = str(port).strip()
        pwd = str(pwd).strip()
        tStart = time.time()
        # if ip == '' or port == '' or user == '' or pwd == '': return False
        self.port = str(port).replace(' ', '')
        self.ip = str(ip).replace(' ', '')
        self.user = str(user).replace(' ', '')
        self.pwd = str(pwd).replace(' ', '')
        self.port = int(port)
        self.timeout = int(timeout)
        self.env = env
        logger.debug('%s,%s,%s,%s' % (self.ip, self.port, self.user, self.pwd))
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(self.ip, self.port, self.user, self.pwd, timeout=self.timeout, banner_timeout=10,auth_timeout=10)

        logger.debug('%s,%s,%s,%s,用时：%s' % (self.ip, self.port, self.user, self.pwd, time.time() - tStart))
        return self.ssh

    def execute(self, cmd, log=True):
        """
        | ##@函数目的: SSH执行命令
        | ##@参数说明：
        | ##@返回值：命令执行结果
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        work.exec_command('source ~/.bashrc; cd /;ll')
        """
        tStart = time.time()

        logger.debug('sshExec -> %s' % (cmd))
        # 解决环境变量问题
        env = 'source .bash_profile;source /etc/profile;export LANG=en_US.UTF-8;'
        stdin, stdout, stderr = self.ssh.exec_command('%s%s' % (env, cmd))
        stdin.write("n")
        returnMsg = ''.join(stdout.read() + stderr.read())
        if log: logger.debug('SSH返回:\n%s用时：%s' % (returnMsg, time.time() - tStart))
        returnMsg = str(returnMsg).strip()
        return returnMsg

    def execute_by_channel(self, cmd, log=False):
        """
        通过channel 获取到执行命令的 exit code
        @author： lanxiong
        @time：2018/10/10
        """
        bufsize = -1
        tStart = time.time()
        logger.debug('sshExec -> %s' % (cmd))
        # 解决环境变量问题
        env = 'source .bash_profile;source /etc/profile;export LANG=en_US.UTF-8;'
        chan = self.ssh.get_transport().open_session()
        chan.exec_command('%s%s' % (env, cmd))
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('r', bufsize)
        stderr = chan.makefile_stderr('r', bufsize)
        stdin.write("n")
        returnMsg = ''.join(stdout.read() + stderr.read())
        if log: logger.debug('SSH返回:\n%s用时：%s' % (returnMsg, time.time() - tStart))
        returnMsg = str(returnMsg).strip()
        return chan.recv_exit_status(), returnMsg

    def close(self):
        '''
        关闭ssh
        '''
        self.ssh.close()



class ClassSCP:
    '''
    scp 类
    '''

    def __init__(self):
        self.ip = None
        self.port = None
        self.user = None
        self.pwd = None
        self.ssh = None
        self.sftp = None

    @ssh_pwd_decrypt
    def open(self, ip, port, user, pwd):
        '''
        打开ssh ,用于上传
        '''
        ip = str(ip).strip()
        port = str(port).strip()
        pwd = str(pwd).strip()
        self.ip = ip
        self.port = int(port)
        self.ssh = paramiko.Transport((self.ip, self.port))
        self.user = user
        self.pwd = pwd

        logger.debug('%s,%s,%s,%s' % (self.ip, self.port, self.user, self.pwd))
        self.ssh.connect(username=self.user, password=pwd)
        self.sftp = paramiko.SFTPClient.from_transport(self.ssh)
        return self.sftp, self.ssh

    def download_file(self, remote_path, file_path):
        """
        | ##@函数目的: SSH下载文件
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        logger.debug('%s to %s' % (remote_path, file_path))
        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.sftp.get(remote_path, file_path)
        return file_path, remote_path

    def upload_file(self, file_path, remote_path):
        """
        | ##@函数目的: SSH上传文件
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        remote_path = str(remote_path).strip()
        file_path = str(file_path).strip()
        if not os.path.isfile(file_path):
            # logger.error('本地文件不存在：%s' % (file_path))
            raise Exception('本地文件不存在：%s' % (file_path))
        logger.debug(
            '%s(size:%s) to %s' % (
                file_path, covert_bytes(int(get_file_size(file_path))), remote_path))

        self.sftp.put(file_path, remote_path)
        return file_path, remote_path

    def close(self):
        '''
         关闭ssh
        '''
        self.sftp.close()
        self.ssh.close()
