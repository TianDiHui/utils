# -*- coding: utf-8 -*-
import os
import tempfile

from file_util import file_writes
from shell_util import exec_shell


class CurlClass():
    # curl 命令的简单封装


    def __init__(self):
        self.cookieFile = tempfile.mktemp()  # 创建名称唯一的临时文件供使用

    def basic_auth(self, URL, username, passwd):
        """
        |##@Function purpose：基础HTTP认证方式登陆
        |##@Parameter description：None
        |##@Return value：None
        |##@Function logic：None
        |##@author： jhuang
        |##@time：2017/6/5
        """

        exec_shell('curl  -u %s:%s  -L -c %s --user-agent Mozilla/4.0 %s' % (username, passwd, self.cookieFile, URL))

    def download(self, URL, saveFile, maxtime=60 * 60, shellFile=True):
        """
        |##@Function purpose：download
        |##@Parameter description：None
        |##@Return value：None
        |##@Function logic：None
        |##@author： jhuang
        |##@time：2017/6/5
        """
        cmd = 'curl --max-time %s -c  %s -b %s --user-agent Mozilla/4.0  -o "%s"  "%s"  ' % (
            maxtime, self.cookieFile, self.cookieFile, saveFile, URL)
        if shellFile:
            shelFile = tempfile.mktemp()
            file_writes(shelFile, cmd)
            os.system('sh %s' % (shelFile))
        else:
            exec_shell(cmd, timeout=maxtime)

    def close(self):
        """
        |##@Function purpose：清理cookie
        |##@Parameter description：None
        |##@Return value：None
        |##@Function logic：None
        |##@author： jhuang
        |##@time：2017/6/5
        """
        if os.path.isfile(self.cookieFile):
            os.remove(self.cookieFile)
