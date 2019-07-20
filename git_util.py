# -*- coding: utf-8 -*-
# 官方文档 ：http://gitpython.readthedocs.io/en/stable/tutorial.html
# 配置ssh ： https://segmentfault.com/a/1190000002645623
"""
| ##@函数目的: git 操作类
| ##@参数说明：
| ##@返回值：
| ##@函数逻辑：
| ##@开发人：jhuang
| ##@时间：
"""

# ===============================================================================
# repo=GitClass()
# logger.info  ( str(repo.status())
# repo.commits(u'git测试')
# ===============================================================================

import re

from coverage.control import os

from SRMCenter.apps.global_var import  GlobalVar
logger = logging.getLogger('django')
from shell_util import exec_shell, subprocess_to_log


class GitClass():
    def __init__(self, LocalRepoPath=None):
        gitLog = os.path.join(GlobalVar.project_dir_log, '', 'git.log')
        self.gitLog = gitLog
        self.LocalRepoPath = LocalRepoPath
        ret = exec_shell('git --version')
        logger.debug('Git版本:%s' % ret['msg'])
        if not os.path.isdir(LocalRepoPath):
            logger.debug('创建GIT仓库根目录:%s' % LocalRepoPath)
            os.makedirs(LocalRepoPath)

            # raise Exception(u'GIT仓库路径不存在:%s' % LocalRepoPath)

    def version(self):
        """
        | ##@函数目的: 获得git 版本
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        ret = exec_shell('git --version')
        return ret['msg']

    def branch(self):
        """
        | ##@函数目的: 获得分支信息
        | ##@参数说明：
        | ##@返回值：数组,每个元素在数组内
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git branch'

        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)

        ret = ret.split('\n')
        # logger.info  ( ret)
        array = []
        for i in range(len(ret) - 1):
            e = str(ret[i]).replace(' ', '')
            array.append(e)
        return array

    def push(self, branch):
        """
        | ##@函数目的: 单个文件提交
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git push --progress  "origin" %s' % (branch)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        return ret

    def config(self, username, email):
        """
        | ##@函数目的: 设置Git的user name和email
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        Git客户端配置
         git config --global user.name "jhuang"
         git config --global user.email "jhuang@cenboomh.com"
         ssh-keygen -t rsa -C "jhuang@cenboomh.com"
         eval "$(ssh-agent -s)"
         ssh-add ~/.ssh/id_rsa_git
         cd 
         vi /root/.ssh/id_rsa.pub
        """

        cmd = 'git config --global user.name "%s"' % (username)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        cmd = 'git config --global user.email "%s"' % (email)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        '''
        如果需要交互可以参考:
        https://pexpect.readthedocs.io/en/stable/overview.html#find-the-end-of-line-cr-lf-conventions
        http://www.ibm.com/developerworks/cn/linux/l-cn-pexpect2/
        import pexpect
        child = pexpect.spawn ('ssh th@192.168.220.54')
        child.sendline ('yes')
        child.sendline ('thzk211!')
        logger.info child.before   # logger.info the result of the ls command.
        child.interact()     # Give control of the child to the user.
        '''
        return ret

    def checkout(self, branch):
        """
        | ##@函数目的: 切换分支
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git checkout %s' % (branch)

        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        if rc == '0':
            logger.debug('切换分支成功...%s' % (branch))
        else:
            raise Exception('切换GIT分支%s失败，请稍等重试！' % (branch))

        return ret

    def status(self):
        """
        | ##@函数目的: 获取待提交的文件列表
        | ##@参数说明：
        | ##@返回值：数组
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git status'
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        rs = re.findall('\s+(\w+\.\w+)', ret, re.S)
        # logger.info  ( rs)
        return rs

    def commits(self, fileLists, comment):
        """
        | ##@函数目的: 将所有改变提交
        | ##@参数说明：git commit -a是把unstaged的文件变成staged（这里不包括新建(untracked)的文件），然后commit
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        arrays = self.status()
        for i in fileLists:
            file_path = i
            self.add(file_path)
        cmd = 'git commit -m "%s"' % (comment)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        cmd = 'git add --all'
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        cmd = 'git commit -a -m "%s"' % (comment)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        return arrays

    def commit(self, comment, file_path):
        """
        | ##@函数目的: 单个文件提交
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        self.add(file_path)
        comment = str(comment).encode('gbk')
        cmd = 'git commit -m %s %s"' % (comment, file_path)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        return ret

    def add_all(self, file_path):
        """
        | ##@函数目的: 添加到本地索引
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git add -A'
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        return ret

    def add(self, file_path):
        """
        | ##@函数目的: 添加到本地索引
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git add %s"' % (file_path)
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        return ret

    def pull(self, branch):
        """
        | ##@函数目的: pull
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        cmd = 'git pull --progress --no-rebase -v "origin" %s' % (branch)
        #         cmd='git pull'
        ret, rc = subprocess_to_log(cmd, self.gitLog, self.LocalRepoPath)
        return ret

    def clone(self, RemoteGitiPath):
        """
        | ##@函数目的: 克隆库
        | ##@参数说明：gitpath : git@192.168.219.41:his/hisdb.git 
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        ret, rc = subprocess_to_log('git clone --progress -v "%s" "%s"' % (RemoteGitiPath, self.LocalRepoPath),
                                    self.gitLog)
        return ret
