# -*- coding: utf-8 -*-
"""
ftp 操作

:param param1: this is a first param
:param param2: this is a second param
:returns: this is a description of what is returned
:raises keyError: raises an exception
@author： jhuang
@time：27/02/2018
"""
from ftplib import FTP


class FtpUtil(object):
    def __init__(self, set_debuglevel=0):
        self.host = None
        self.username = None
        self.password = None
        self.ftp_con = None
        self.set_debuglevel = set_debuglevel
        self.bufsize = 1024

    def connect(self, host, username, password, port=21):
        self.ftp_con = FTP()
        self.ftp_con.set_debuglevel(self.set_debuglevel)  # 打开调试级别2，显示详细信息
        self.ftp_con.connect(host, port)  # 连接
        self.ftp_con.login(username, password)  # 登录，如果匿名登录则用空串代替即可

    def upload(self, remotepath, localpath):
        fp = open(localpath, 'rb')
        self.ftp_con.set_debuglevel(self.set_debuglevel)

        self.ftp_con.storbinary('STOR ' + remotepath, fp, self.bufsize)  # 上传文件
        fp.close()

    def delete(self, filename):
        res = self.ftp_con.delete(filename)
        return res

    def mkd(self, filename):
        res = self.ftp_con.mkd(filename)
        return res

    def quit(self):
        """
        退出FTP连接

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：27/02/2018
        """
        self.ftp_con.quit()
