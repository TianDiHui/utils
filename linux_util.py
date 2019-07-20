# -*- coding: utf-8 -*-
import platform
import time

import psutil


def is_linux_system():
    """
    | ##@函数目的: 获取系统是否为linux
    | ##@参数说明：True or False
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    return platform.system() in ['Linux','Darwin']


class LinuxInfo(object):
    def boot_time_stat(self):
        """
        | ##@函数目的: 系统启动时间点
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        uptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
        return uptime

    def uptime_stat(self):
        """
        | ##@函数目的: 获取系统已运行时间
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        uptime = {}
        if is_linux_system() is True:
            f = open("/proc/uptime")
            con = f.read().split()
            f.close()
            all_sec = float(con[0])
            MINUTE, HOUR, DAY = 60, 3600, 86400
            uptime['day'] = int(all_sec / DAY)
            uptime['hour'] = int((all_sec % DAY) / HOUR)
            uptime['minute'] = int((all_sec % HOUR) / MINUTE)
            uptime['second'] = int(all_sec % MINUTE)
            uptime['Free rate'] = float(con[1]) / float(con[0])
        return uptime

    def load_stat(self):
        """
        | ##@函数目的: 获取系统负载
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        loadavg = {}
        if is_linux_system() is True:
            f = open("/proc/loadavg")
            con = f.read().split()
            f.close()
            loadavg['lavg_1'] = con[0]
            loadavg['lavg_5'] = con[1]
            loadavg['lavg_15'] = con[2]
            loadavg['nr'] = con[3]
            loadavg['last_pid'] = con[4]
        else:
            loadavg['lavg_1'] = 0
            loadavg['lavg_5'] = 0
            loadavg['lavg_15'] = 0
            loadavg['nr'] = 0
            loadavg['last_pid'] = 0

        return loadavg

    def mem_and_swap(self):
        """
        | ##@函数目的: 获取内存和SWAP
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        loadavg = {}
        if is_linux_system() is True:
            f = open("proc/meminfo")
            con = f.read().split()
            f.close()
            loadavg['SwapTotal'] = con[0]
            loadavg['SwapCached'] = con[1]
            loadavg['MemTotal'] = con[2]
            loadavg['MemFree'] = con[3]
        print loadavg
        return loadavg
