# -*- coding: utf-8 -*-
import json
import os
import re
import socket
import telnetlib
import threading
import urllib2
from time import sleep

import psutil
from utils.common_util import get_except
from django.core.mail.message import EmailMultiAlternatives
from linux_util import is_linux_system
logger = logging.getLogger('django')
from decorator_util import async
from shell_util import exec_shell
from string_util import covert_bytes


def ping_test(host, ping_count='2'):
    """
    ping

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: True 主机Ping 通
    :raises keyError: raises an exception
    @author： jhuang
    @time：01/03/2018
    """
    import subprocess
    with open(os.devnull, "wb") as limbo:
        parm_count = '-n'
        if is_linux_system():
            parm_count = '-c'
        result = subprocess.Popen(["ping", parm_count, ping_count, host], stdout=limbo, stderr=limbo).wait()
        if result:
            print host, "inactive"
            return False
        else:
            print host, "active"
            return True


def get_host_all_ip():
    """
       获取主机全部IP地址

       :param param1: this is a first param
       :param param2: this is a second param
       :returns: ip list
       :raises keyError: raises an exception
       @author： jhuang
       @time：05/02/2018
    """

    ip_list = []

    if is_linux_system():
        ip_dic = exec_shell(
            "/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d 'addr:'")
        ip_list = str(ip_dic['msg']).split('\n')
    else:
        hostname = socket.gethostname()
        addrs = socket.getaddrinfo(hostname, None)
        for item in addrs:
            if item[0] == 2:
                ip_list.append(item[4][0])
    return ip_list


def get_client_ip(request):
    """
        获取客户端IP
    """
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    return regip


def do_telnet(Host, username, password, finish, commands):
    '''''Telnet远程登录：Windows客户端连接Linux服务器'''

    # 连接Telnet服务器
    tn = telnetlib.Telnet(Host, port=23, timeout=10)
    tn.set_debuglevel(2)

    # 输入登录用户名
    tn.read_until('login: ')
    tn.write(username + '\n')

    # 输入登录密码
    tn.read_until('password: ')
    tn.write(password + '\n')

    # 登录完毕后执行命令
    tn.read_until(finish)
    for command in commands:
        tn.write('%s\n' % command)

        # 执行完毕后，终止Telnet连接（或输入exit退出）
    tn.read_until(finish)
    tn.close()  # tn.write('exit\n')


def get_remote_file_size(url, proxy=None):
    """ 通过content-length头获取远程文件大小
        url - 目标文件URL
        proxy - 代理
        :rtype: object"""
    opener = urllib2.build_opener()
    if proxy:
        if url.lower().startswith('https://'):
            opener.add_handler(urllib2.ProxyHandler({'https': proxy}))
        else:
            opener.add_handler(urllib2.ProxyHandler({'http': proxy}))
    try:
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'
        response = opener.open(request)
        response.read()
    except Exception as e:  # 远程文件不存在
        return 0
    else:
        fileSize = dict(response.headers).get('content-length', 0)
        return int(fileSize)


def get_netspeed(eth=''):
    """
    |##desc: 网卡网速获取
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：2017-07-20
    """
    RX = 0
    TX = 0
    if is_linux_system() is True:
        # return RX, TX
        if eth == '':
            eth = psutil.net_io_counters(pernic=True).keys()[1]

        ret = exec_shell('/sbin/ifconfig %s | grep bytes' % (eth))
        X1 = re.findall('bytes.(\d+)', ret['msg'])

        sleep(1)

        ret = exec_shell('/sbin/ifconfig %s | grep bytes' % (eth))
        X2 = re.findall('bytes.(\d+)', ret['msg'])
        print X2
        if len(X2) > 0:
            # RX 为下行流量 TX 为上行流量
            RX = covert_bytes(int(X2[0]) - int(X1[0]))
            TX = covert_bytes(int(X2[1]) - int(X1[1]))
        print RX, RX
    return RX, TX


def get_ip_isp(ip):
    try:
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip='
        response = urllib2.urlopen(url + ip, timeout=10)
        result = response.readlines()
        data = json.loads(result[0])
        isp = "%s-%s-%s" % (data['data']['region'], data['data']['city'], data['data']['isp'])
        #         logger.debug('IP:%s,ISP:%s' %(ip,isp))
        return isp
    except:
        return ''

@async
def send_mail(subject, text_content, html_content, to_email_list, attach_file='',DEFAULT_FROM_EMAIL=None):
    """
    |##@函数目的：发送邮件  子函数，要调用请使用上面的 sendmail
    |##@返回值：
    |##@函数逻辑：无
    |##@开发人：jhuang，rksun
    |##@时间：
    |##@参数说明：
        subject 邮件标题
        text_content 邮件正文
        html_content HTML版本邮件正文
        to_email_list ['first@example.com', 'other@example.com']

        send_mail('test','test','test',['376667689@qq.com'])
    """
    if isinstance(to_email_list, list) is False and to_email_list != None:
        lists = []
        lists.append(to_email_list)
        to_email_list = lists
    try:
        to_email_list = list(set(to_email_list))
        if '' in to_email_list:
            to_email_list.remove('')
        # to_email_list.remove(None)
        if len(to_email_list) > 0:

            logger.debug('发送邮件至:%s,邮件标题:%s' % (to_email_list, subject))
            # http://python.usyiyi.cn/documents/django_182/topics/email.html

            if html_content != '':
                text_content = html_content
            msg = EmailMultiAlternatives(subject, text_content, DEFAULT_FROM_EMAIL, to_email_list)
            msg.encoding = 'utf-8'
            if html_content != '':
                msg.attach_alternative(html_content, "text/html")
            if os.path.isfile(attach_file):
                logger.debug('添加附件:%s' % (attach_file))
                msg.attach_file(attach_file)
            msg.send()
        else:
            logger.debug('邮件发送目标邮箱列表为空,邮件标题:%s' % (subject))
    except:
        logger.exception('发送邮件失败至:%s' % (to_email_list))
