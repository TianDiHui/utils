# -*- coding: utf-8 -*-
'''
@author: lanxiong lanxiong@cenboomh.com
@file: docker_util.py
@time: 2018/11/29 18:45
@desc:
'''
from .ssh_util import ClassSSH


class DockerUtil(object):
    def __init__(self, host_ip, host_port, host_user, host_pwd):
        self.host_ip = host_ip
        self.host_port = host_port
        self.host_user = host_user
        self.host_pwd = host_pwd
        self.myssh = None
        self.__initialize()

    def __initialize(self):
        self.myssh = ClassSSH()
        self.myssh.open(self.host_ip,
                        self.host_port,
                        self.host_user,
                        self.host_pwd
                        )

    def get_container_ip(self, container_name_or_id):
        cmd = "env docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' %s" % container_name_or_id
        exit_code, msg = self.myssh.execute_by_channel(cmd)
        if exit_code == 0 or exit_code == '0':
            return msg
        else:
            return ''
        self.myssh.close()
