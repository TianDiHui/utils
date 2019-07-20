# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
import math
import re
import time
import urllib
import uuid

import html2text
import sqlparse
import xmltodict


def string_hash_to_md5(str):


    """
    将字符串HASH

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：09/05/2018
    """
    return  hashlib.md5(str.encode("utf8")).hexdigest()

def sqlparse_split(sql):
    """
    SQL分句，解决存储过程问题

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：26/04/2018
    """
    sql_list = sqlparse.split(sql)
    sql_list_new = []
    list_tmp = []
    for r in sql_list:
        sql_line = r

        re_sql = re.findall('(?:declare|begin).*?', sql_line.lower())
        if len(re_sql) > 0:
            list_tmp.append(sql_line)
            continue

        re_sql = re.findall('.*?end;$', sql_line.lower())
        if len(re_sql) > 0:
            list_tmp.append(sql_line)
            sql_list_new.append('\n'.join(list_tmp))
            list_tmp = []
            continue

        if len(list_tmp) > 0:
            list_tmp.append(sql_line)
        else:
            sql_list_new.append(sql_line)
            continue
    return sql_list_new


def list_diff(index, a_list, b_list):
    """
        list 集合处理

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：12/25/2017
    """

    if index == 0:
        # 差集合
        ret_list = list(set(a_list) ^ set(b_list))
    elif index == 1:
        # 合集
        ret_list = list(set(a_list).union(set(b_list)))
    elif index == 2:
        # 交集
        ret_list = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
    return ret_list


def grep(str, findstr):
    """
    |##desc: 模拟grep命令
    |##:param: None
    |##:return: None
    |##@author： jhuang
    |##@time：12/6/2017
    """
    return "\n".join(re.findall('.*' + findstr + '.*', str))


def covert_bytes(bytes, lst=['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']):
    """
        |##desc: 单位转换
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：2017-07-20
        """
    # print bytes
    if bytes <= 0:
        bytes = 1
    i = int(math.floor(  # 舍弃小数点，取小
        math.log(bytes, 1024)  # 求对数(对数：若 a**b = N 则 b 叫做以 a 为底 N 的对数)
    ))

    if i >= len(lst):
        i = len(lst) - 1
    return ('%.2f' + " " + lst[i]) % (bytes / math.pow(1024, i))


def string_replace_re(pattern, replace_str, str):
    """
    正则字符串替换

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：12/03/2018
    """
    out = re.sub(pattern, replace_str, str)
    print out


def add_quote(c):
    """
    |##@函数目的：与map联合使用给list 元素增引号
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：无
    |##@开发人：jhuang
    |##@时间：
    """
    return '%s%s%s' % ('"', c, '"')


def time_now_str():
    """格式化成2016-03-20 11:45:39形式"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def xml_to_json(xmlStr):
    """
    | ##@函数目的: xml_to_json
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    convertedDict = xmltodict.parse(xmlStr)
    jsonStr = json.dumps(convertedDict)
    jsonStr = json.loads(jsonStr)

    return jsonStr


def url_encode(s):
    """
    | ##@函数目的: URL编码
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    return urllib.quote(str(s))


def url_decode(s):
    """
    | ##@函数目的: URL解码
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    return urllib.unquote(str(s))


def html_strip_tag(html, strp_use_re=True):
    """
    | ##@函数目的: 去除html标签
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    if strp_use_re:
        # 正则替换
        html = re.compile('<a[^>]*>').sub('', html)
        html = re.compile('<\/a>').sub('', html)

    html = html2text.html2text(html)
    return html


def get_stamp_now():
    """
    | ##@函数目的: 返回时间戳，默认是当前时间
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    return int(time.mktime(datetime.datetime.now().timetuple()))


def dbtime_to_timestamp(strdate):
    """
    | ##@函数目的: 普通时间（支持str(dbdatetime)转时间时间戳）
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    if strdate == '': return ''
    get_stamp_now = time.mktime(time.strptime(strdate, '%Y-%m-%d %H:%M:%S'))
    return int(get_stamp_now)


def timestamp_to_dbtime(stampTime):
    """
    | ##@函数目的: 时间戳转时间
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    x = time.localtime(float(stampTime))
    return time.strftime('%Y-%m-%d %H:%M:%S', x)


def time_to_db(sTime=None):
    """
        当前系统时间(用于插入数据库)
    """
    if sTime == None or sTime == '':
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S');
    else:

        if isinstance(sTime, str) is True:

            t = sTime.strptime('%Y-%m-%d %H:%M:%S')
        else:
            t = datetime.datetime.strptime(sTime, '%Y-%m-%d %H:%M:%S')
    return t


def get_now_time():
    """
        格式化时间，主要用于作为文件名
        2017-01-03 15:51:30.743000 
        主意，此函数不能用于存入数据库字段 ！ by juang
    """
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S');


def get_uuid(retStringType=True):
    """
        创建UUUI
    """
    uuid1 = uuid.uuid4()
    if retStringType:
        return str(uuid1)
    else:
        return uuid1
        # logger.info u'生成UUID:%s' % uuid1
