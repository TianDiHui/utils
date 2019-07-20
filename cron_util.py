# -*- coding: utf-8 -*-
import re
from datetime import datetime

from croniter import croniter

from utils.common_util import get_except
from utils.file_util import file_reads, file_writes


def crontab_item_remove(crontab_item, log_user='root'):
    """
    |##desc: 删除计划任务，需要ROOT权限
    |##:param: log_user 添加到什么用户下面去
    |##:return: None
    |##@author： jhuang
    |##@time：9/1/2017
    """
    crontabFile = "/var/spool/cron/%s" % (log_user)
    crontabs = file_reads(crontabFile)
    crontabsList = crontab_parse(crontabs, True)
    if crontab_item in crontabsList:
        crontabsList.remove(crontab_item)
    crontabs = '\n'.join(crontabsList)
    file_writes(crontabFile, crontabs + '\n')


def crontab_item_add(crontab_item, log_user='root'):
    """
    |##desc: 添加计划任务，需要ROOT权限
    |##:param: log_user 添加到什么用户下面去
    |##:return: None
    |##@author： jhuang
    |##@time：9/1/2017
    """
    crontabFile = "/var/spool/cron/%s" % (log_user)
    crontabs = file_reads(crontabFile)
    crontabsList = crontab_parse(crontabs, True)
    if crontab_item in crontabsList:
        crontabsList.remove(crontab_item)
    crontabsList.append(crontab_item)
    crontabs = '\n'.join(crontabsList)
    file_writes(crontabFile, crontabs + '\n')


def get_crond_next_time(interval, count=5):
    """
    |##@Function purpose：计算下次执行时间
    |##@Parameter description：None
    |##@Return value：None
    |##@Function logic：None
    |##@author： jhuang
    |##@time：
    """
    timeList = []
    iter = croniter(interval)
    for i in range(count):
        next_date = iter.get_next(datetime)
        next_date = datetime.strftime(next_date, '%Y-%m-%d %H:%M:%S')
        timeList.append(next_date)
    return timeList


def crontab_parse(crontabs, LineList=False):
    """
    |##@Function purpose：解析Crontab
    |##@Parameter description：None
    |##@Return value：None
    |##@Function logic：None
    |##@author： jhuang
    |##@time：
    """
    try:
        print crontabs
        crontabs = re.findall('^(?:\d+|\*).*?\s+.*?\s+.*?\s+.*?\s+.*?\s+.*', crontabs, re.M)
        crontab_list = []
        if LineList:
            for r in crontabs:
                crontab_list.append(r.strip().strip('\n').strip('\r'))
            return crontab_list

        print crontabs
        for crontab in crontabs:
            dic = {}
            # print crontab
            dic['interval'] = str(
                re.findall('(^(?:\d+|\*).*?\s+.*?\s+.*?\s+.*?\s+.*?\s+)(.*)', crontab, re.M)[0][0]).strip().strip(
                '\n').strip('\r')
            dic['what'] = str(
                re.findall('(^(?:\d+|\*).*?\s+.*?\s+.*?\s+.*?\s+.*?\s+)(.*)', crontab, re.M)[0][1]).strip().strip(
                '\n').strip('\r')
            crontab = crontab.replace(' ', '')
            crontab_list.append(dic)
        return crontab_list
    except Exception as e:
        get_except(e)
        return []
