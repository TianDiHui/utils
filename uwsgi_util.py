# -*- coding: utf-8 -*-
from linux_util import is_linux_system
logger = logging.getLogger('django')
from shell_util import exec_shell


class Uwsgi(object):
    def __init__(self):
        pass

    def is_master_process(self, uwsgi_server_port='8002'):
        """
        判断自身是否为uwsgi 中的mater 进程

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：9/26/2018
        """

        import os

        self.self_pid = str(os.getpid())
        if is_linux_system():
            self.uwsgi_master_pid = str(exec_shell(
                """netstat -anp|grep %s|awk '{printf $7}'|cut -d/ -f1""" % (uwsgi_server_port))['msg'])
            self.self_ppid = str(os.getppid())
        else:
            self.self_ppid = '-1'
            self.uwsgi_master_pid = '0'

        logger.debug('uwsgi_master_pid:{uwsgi_master_pid},self_ppid:{self_ppid},self_pid:{self_pid}'.format(
            uwsgi_master_pid=self.uwsgi_master_pid,
            self_ppid=self.self_ppid, self_pid=self.self_pid))
        if self.uwsgi_master_pid == self.self_ppid:
            return True
        else:
            return False
