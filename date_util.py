# -*- coding: utf-8 -*-
import calendar
import datetime

import pandas as pd
from flask import json

from db_util import sql_to_list
from http_util import HttpClass
import time


def date_time_now():
    """
    当前时间，用于写入数据库 字段类型是 TIMESTAMP

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: date 类型
    :raises keyError: raises an exception
    @author： jhuang
    @time：03/04/2018
    """
    return datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')


def get_week_day(date):
    """
    获取指定日期是星期几

    print(get_week_day(datetime.datetime.now()))
    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：03/05/2018
    """
    week_day_dict = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    day = date.weekday()
    return week_day_dict[day]


def get_day_work(date):
    """
    获取指定日期是星期几

    print(get_week_day(datetime.datetime.now()))
    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：03/05/2018
    """
    week_day_dict = {
        0: '一',
        1: '二',
        2: '三',
        3: '四',
        4: '五',
        5: '六',
        6: '日',
    }
    day = date.weekday()
    return week_day_dict[day]


def week_of_month():
    """
    获取本月第几周

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：03/05/2018
    """
    day_of_month = datetime.datetime.now().day
    week_number = (day_of_month - 1) // 7 + 1
    return week_number


def get_int_md(year=None, month=None):
    """
    返回本月天数
    :return:
    """
    if year == None or month == None:
        today = datetime.datetime.today()
    else:
        today = datetime.datetime(int(year), int(month), 1)
    month = calendar.monthrange(today.year, today.month)[1]
    return month


def get_this_month(year=None, month=None):
    """
    默认返回本月双休天数以及具体哪些天，返回指定年月的双休日
    :return:{total: ,day:}
    """
    if year == None or month == None:
        today = datetime.datetime.today()
    else:
        today = datetime.datetime(int(year), int(month), 1)

    month_of_days_all_swap = {'vacation': []}
    vacation = 0

    get_int_md_day = calendar.monthrange(today.year, today.month)[1] + 1
    month_of_days_all = range(1, get_int_md_day)

    for month_of_days in month_of_days_all:

        appointed_day = datetime.date(today.year, today.month, month_of_days)
        if appointed_day.weekday() == 5 or appointed_day.weekday() == 6:
            month_of_days_all_swap['vacation'].append(appointed_day)
            vacation += 1

    month_of_days_all_swap['total'] = vacation

    return month_of_days_all_swap


def get_interval_vacation(start_date, end_date):
    """
    获取区间双休日
    :param start_date:开始时间   str(2017-01-01)
    :param end_date: 结束时间   str(2017-01-01)
    :return:{(number of days),{day1,day2,..}}
    liww
    """
    interval_date = []
    appointed_day_vacation = {'vacation': []}

    sql = """
    SELECT a.date FROM holidays_and_festivals a
    WHERE a.`type` = '2'"""
    sql_list = sql_to_list(sql)

    for x in list(pd.date_range(start=start_date, end=end_date)):
        x_row = 0
        for sql_list_one in sql_list:
            if sql_list_one['date'].year == x.year and sql_list_one['date'].month == x.month and sql_list_one[
                'date'].day == x.day:
                x_row = 1
                break
        if x_row == 0:
            interval_date.append(x)

    for appointed_day in interval_date:
        if appointed_day.weekday() == 5 or appointed_day.weekday() == 6:
            switch_day = datetime.date(appointed_day.year, appointed_day.month, appointed_day.day)
            appointed_day_vacation['vacation'].append(switch_day)

    appointed_day_vacation['total'] = len(interval_date)

    return appointed_day_vacation


def get_holiday_work(year, month):
    """
    获取双休却需要上班的日子
    :param year:
    :param month:
    :return:
    liww
    """
    go_to_work = []
    sql = "SELECT a.date FROM holidays_and_festivals a WHERE	date_format(a.date,'%%Y-%%m')='%s-%s' AND a.type = '2'" % (
    year, month)
    holidays_and_festivals = sql_to_list(sql, None, True)
    for holidays_and_festivals_one in holidays_and_festivals:
        go_to_work.append(holidays_and_festivals_one['date'])

    return go_to_work


def get_festival_insert(year):
    """
    获取今年的双休外的节假日写入数据库
    :return:
    """
    ohttp = HttpClass()
    get_date = ohttp.get('http://tool.bitefu.net/jiari/?d=%s' % year)
    get_date = json.loads(get_date[1])['%s' % year]
    for get_date_one in get_date:
        date_day = ('%s' % year) + get_date_one
        sql = "INSERT INTO `holidays_and_festivals` (`date`,`type`) VALUES ('%s','1')" % date_day
        sql_to_list(sql, None, True)
    return 1


def get_festival_by_year(year):
    """
    获取指定年的节假日
    @author： lanxiong
    @time：2018/8/21
    """
    sql = "SELECT date,type FROM holidays_and_festivals WHERE	date_format(date,'%%Y-')='%s-'" % (year)
    holidays_and_festivals = sql_to_list(sql)
    return holidays_and_festivals

def get_festival_by_date_range(start_date, end_date):
    sql = """
        SELECT
            date, type
        FROM
            holidays_and_festivals
        WHERE
            date between'{start_date}' and '{end_date}'
    """.format(start_date=start_date, end_date=end_date)
    holidays_and_festivals = sql_to_list(sql)
    return holidays_and_festivals

def get_festival(year, month, is_legal=False):
    """
    获取数据库中某月所有非双休假日
    :param year:
    :return:
    """
    holidays_and_festivals_list = []
    if is_legal:
        # 法定需要加工资的日子
        sql = "SELECT a.date FROM holidays_and_festivals a WHERE	date_format(a.date,'%%Y-%%m')='%s-%s' AND a.type = '1' AND a.legal=1" % (
    year, month)
    else:
        sql = "SELECT a.date FROM holidays_and_festivals a WHERE	date_format(a.date,'%%Y-%%m')='%s-%s' AND a.type = '1'" % (
            year, month)
    holidays_and_festivals = sql_to_list(sql, None, True)
    for holidays_and_festivals_one in holidays_and_festivals:
        holidays_and_festivals_list.append(holidays_and_festivals_one['date'])

    return holidays_and_festivals_list


def get_interval_festival(start_date, end_date):
    """
    获取区间数据库非双休假日
    :param start_date:开始时间   str(2017-01-01)
    :param end_date: 结束时间   str(2017-01-01)
    :return:{(number of days),{day1,day2,..}}
    liww
    """
    interval_date = []
    holidays_and_festivals = []
    appointed_day_vacation = {'vacation': []}

    for x in list(pd.date_range(start=start_date, end=end_date)):
        switch_day = datetime.date(x.year, x.month, x.day)
        # switch_day = datetime.datetime.strftime(x, '%Y-%m-%d')
        interval_date.append(switch_day)

    sql = "SELECT a.date FROM holidays_and_festivals a where type = 1"
    sql_list = sql_to_list(sql, None, True)

    for x in sql_list:
        switch_day = datetime.date(x['date'].year, x['date'].month, x['date'].day)
        # switch_day = datetime.datetime.strftime(x['date'], '%Y-%m-%d')
        holidays_and_festivals.append(switch_day)

    for holidays_and_festivals_one in holidays_and_festivals:
        if holidays_and_festivals_one in interval_date:
            appointed_day_vacation['vacation'].append(holidays_and_festivals_one)

    appointed_day_vacation['total'] = len(appointed_day_vacation['vacation'])

    return appointed_day_vacation


def convert_timestamp_to_date(timestamp, date_format="%Y-%m-%d %H:%M:%S"):
    """
    毫秒转日期
    @author： lanxiong
    @time：2018/8/15
    """
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime(date_format)


def convert_date_to_timestamp(mydate, date_format="%Y-%m-%d %H:%M:%S"):
    """
    日期转时间戳 秒
    @author： lanxiong
    @time：2018/8/20
    """
    dt = datetime.datetime.strptime(mydate, date_format)
    timestamp = time.mktime(dt.timetuple())
    return timestamp


def get_datetime_num_days(num, date_format="%Y-%m-%d %H:%M:%S"):
    """
    获取num天前/后的日期
    @author： lanxiong
    @time：2018/8/16
    """
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=num)
    n_days = now + delta
    return n_days.strftime(date_format)


def get_date_range(beginDate, endDate, date_format="%Y-%m-%d %H:%M:%S"):
    dates = []
    dt = datetime.datetime.strptime(beginDate, date_format)
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime(date_format)
    return dates


def get_date_by_month(year, month, date_format="%Y-%m-%d", get_timestamp=False):
    num_list = range(calendar.monthrange(year, month)[1] + 1)[1:]
    date_list = list()
    for i in num_list:
        date_list.append(datetime.datetime(year, month, i).strftime(date_format))
    if get_timestamp:
        # 获取毫秒时间戳
        return [int(convert_date_to_timestamp(i, date_format) * 1000) for i in date_list]
    else:
        return date_list


def get_working_time(onduty_time, offduty_time, work_date):
    """
    提供上下班打卡时间，计算工作时长
    onduty_time 上班打卡时间， 时间戳毫秒
    offduty_time 下班打卡时间， 时间戳毫秒
    work_date 工作日 '2018-10-10'
    @author： lanxiong
    @time：2018/11/15
    print get_working_time(1538355625000, 1538388501000, '2018-10-01')
    """
    from interval import IntervalSet
    #TODO;从参数表获取
    onduty_time = onduty_time / 1000
    offduty_time = offduty_time / 1000
    work_date = convert_timestamp_to_date(work_date, date_format="%Y-%m-%d")
    am_onduty_time = "00:00"
    am_offduty_time = "12:00"
    pm_onduty_time = "13:30"
    pm_offduty_time = "23:59"
    am_onduty_time_stamp = convert_date_to_timestamp(work_date + ' ' + am_onduty_time, date_format="%Y-%m-%d %H:%M")
    am_offduty_time_stamp = convert_date_to_timestamp(work_date + ' ' + am_offduty_time, date_format="%Y-%m-%d %H:%M")
    pm_onduty_time_stamp = convert_date_to_timestamp(work_date + ' ' + pm_onduty_time, date_format="%Y-%m-%d %H:%M")
    pm_offduty_time_stamp = convert_date_to_timestamp(work_date + ' ' + pm_offduty_time, date_format="%Y-%m-%d %H:%M")

    am_work = IntervalSet.between(am_onduty_time_stamp, am_offduty_time_stamp)
    lunch_time = IntervalSet.between(am_offduty_time_stamp, pm_onduty_time_stamp)
    pm_work = IntervalSet.between(pm_onduty_time_stamp, pm_offduty_time_stamp)

    if offduty_time in am_work:
        return offduty_time - onduty_time
    elif offduty_time in lunch_time:
        return am_offduty_time_stamp - onduty_time
    elif offduty_time in pm_work:
        if onduty_time in am_work:
            return offduty_time - onduty_time - 1.5*60*60
        elif onduty_time in lunch_time:
            return offduty_time - pm_onduty_time_stamp
        elif onduty_time in pm_work:
            return offduty_time - onduty_time
    else:
        # 干到第二天了
        return offduty_time - onduty_time

