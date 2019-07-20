# -*- coding: utf-8 -*-

import datetime
import decimal
import json
import logging
import os
import platform
import time
from subprocess import call

import pip
import psutil
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from utils.except_util import GetException


from utils.file_util import file_reads, file_writes
logger = logging.getLogger('django')


# def logging(level):
#     def wrapper(func):
#         def inner_wrapper(*args, **kwargs):
#             print "[{level}]: enter function {func}()".format(
#                 level=level,
#                 func=func.__name__)
#             return func(*args, **kwargs)
#         return inner_wrapper
#     return wrapper


def view_except(error_code=99):
    """
        装饰器，视图异常捕获

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: 返回json格式的异常到前台
        :raises keyError: raises an exception
        @author： jhuang
        @time：08/02/2018
    """

    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            try:
                start_time = time.time()

                ret = func(*args, **kwargs)
                # logger.debug('函数(%s)用时：%s' % (__name__,time.time() - start_time))
                print ( '函数(%s)用时(s)：%s' % (func.__name__, time.time() - start_time))
                return ret
            except Exception as e:
                # pass
                logger.exception('view_except')

                return response_json(get_except(e), error_code=error_code)

                # re-raise the exception
                raise

        return inner_wrapper

    return wrapper


def server_running():
    """
         一个服务进程（用于做后台任务的进程）是否已经运行中

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: true 运行中，false 未在运行
        :raises keyError: raises an exception
        @author： jhuang
        @time：05/02/2018
    """
    logger.debug('检查工程锁...')
    lock_pid = file_reads('locking.pid').strip().strip('\n').strip('\r')
    if lock_pid == '' or len(lock_pid) > 10 or lock_pid == None:
        lock_pid = 0
    logger.debug('lock_pid:%s' % lock_pid)
    if psutil.pid_exists(int(lock_pid)) == False or lock_pid == 0:
        file_writes('locking.pid', str(os.getpid()))
        return False
    else:
        return True


class PipClass():
    """
        |##desc: pip 操作类
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：11/30/2017
    """

    def __init__(self):
        self.requirements_file = 'requirements.txt'
        self.requirements_file4win = 'requirements_win.txt'

    def requirements_gen(self):
        """
        |##@Function purpose：生成依赖库配置
        |##@Parameter description：None
        |##@Return value：None
        |##@Function logic：None
        |##@author： jhuang
        |##@time：
        """
        if 'Linux' in platform.system():
            nulstr = 'nul'
            os.system('pip freeze > ' % (self.requirements_file))
        else:
            nulstr = '/dev/null'
            os.system('pip freeze > %s' % (self.requirements_file4win))

    def ugrade_all(self):
        """
        |##desc: 更新全部依赖库
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：8/29/2017
        """
        for dist in pip.get_installed_distributions():
            call("pip install --upgrade " + dist.project_name, shell=True)

    def requirement_install(self):
        """
        |##@Function purpose：自动安装缺失的库，根据配置文件
        |##@Parameter description：None
        |##@Return value：None
        |##@Function logic：None
        |##@author： jhuang
        |##@time：
        """
        if 'Linux' not in platform.system():
            os.system('setx PYTHONDONTWRITEBYTECODE x > nul')
        else:
            os.system('export PYTHONDONTWRITEBYTECODE=x >/dev/null')

        if os.path.exists(self.requirements_file):
            # -i http://pypi.douban.com/simple   --trusted-host pypi.douban.com
            os.system('pip install -r ' % (self.requirements_file))


def is_windows_system():
    """
    | ##@函数目的: 获取系统是否为Windows
    | ##@参数说明：True or False
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    return 'Windows' in platform.system()


def get_except(e, error_detail=True, error_html=False, write_log=True):
    """
    | ##@函数目的: 获取异常,并打印异常日志
    | ##@参数说明：
    | ##@返回值：字典类型
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    except_text = GetException(e).get_except(error_detail=True, error_html=False, write_log=True)  # 捕获异常，记录到指定日志句柄
    return except_text


class CJsonEncoder(json.JSONEncoder):  # 继承

    def default(self, obj):  # 重写类default方法
        try:
            if isinstance(obj, datetime.datetime):
                try:
                    str_time = obj.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    logger.exception('转换错误')
                    str_time = str(obj)
                finally:
                    return str_time

            elif isinstance(obj, datetime.date):
                return obj.strftime('%Y-%m-%d')
            elif isinstance(obj, decimal.Decimal):

                return str(obj)
            else:
                return json.JSONEncoder.default(self, obj)
        except Exception as e:
            return '无法序列化的对象:%s' % (get_except(e))


def response_json(data, error_code=0, indent=-1, _status_code=None, help_url=None):
    """
    | ##@函数目的: 返回list jsons 数据到前台  ( 推荐 )
    | ##@参数说明：
        data_structure_type: 返回的数据结构类型 ；0（默认）表示不包含total,error_code关键字,1 表示包含total,error关键字，可用于list列分页
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    list_data = []

    if _status_code is not None:
        status_code = _status_code
    else:
        status_code = 200

    if error_code == -1:
        error_code = 0
    if error_code == 0:  # 没有发生错误
        list_data = data
        status_code = 200
    else:  # 历史情况兼容
        dict = {}

        if _status_code is not None:

            status_code = _status_code
        else:
            status_code = 500

        dict['err_code'] = unicode(str(error_code))
        if isinstance(data, str):
            dict['err_msg'] = data.encode('utf-8')

        else:
            dict['err_msg'] = data
        dict['status_code'] = status_code
        dict['help_url'] = help_url
        list_data = dict

    jsondump = json.dumps(list_data, ensure_ascii=False,
                          separators=(',', ':'), cls=CJsonEncoder)
    response = HttpResponse(jsondump, content_type="application/json;charset=utf-8")
    # logger.debug(error_code)

    response.status_code = status_code

    return response


# --------------------------------------------------------------------------------------------------------------
# 不推荐使用
# --------------------------------------------------------------------------------------------------------------
def http_response_json(p_list, success=False, return_list=True, indent=1):
    """
    | ##@函数目的: 返回数据到前台
    | ##@参数说明：需要返回给前台的数据,可以是字符串或数组   ,return_list =True json数组， return_list =False  json字符串
    | ##@返回值：json
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    # t1 = time.time()
    lists = []
    if isinstance(p_list, basestring) is True:
        dic = {}
        dic['msg'] = p_list
        dic['success'] = unicode(str(success))
        if return_list is True:
            lists.append(dic)
            p_list = lists
        else:
            p_list = dic
    jsondump = json.dumps(p_list, indent=indent, cls=DjangoJSONEncoder, ensure_ascii=False,
                          separators=(',', ':'))
    return HttpResponse(jsondump, content_type="application/json;charset=utf-8")


def http_re_json(list_or_dict, errcode='0', indent=0):
    """
    | ##@函数目的: 返回数据到前台
    | ##@参数说明：errcode=0  没有错误>0 存在错误
    | ##@返回值：json
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    t1 = time.time()
    lists = []
    print (type(list_or_dict))

    if isinstance(list_or_dict, list) is True:
        dic = {}
        ListOrDict_new = []
        dic['errcode'] = unicode(str(errcode))
        dic['data'] = list_or_dict
        ListOrDict_new.append(dic)
        list_or_dict = ListOrDict_new

    if isinstance(list_or_dict, basestring) is True or isinstance(list_or_dict, dict) is True:
        dic = {}
        lists = []
        lists.append(list_or_dict)
        ListOrDict_new = []
        dic['errcode'] = unicode(str(errcode))
        dic['data'] = lists
        ListOrDict_new.append(dic)
        list_or_dict = ListOrDict_new

    jsondump = json.dumps(list_or_dict, indent=indent, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(jsondump, content_type="application/json;charset=utf-8")


def http_response_jsons(list_or_dict, success=False, indent=0):
    """
    | ##@函数目的: 返回数据到前台
    | ##@参数说明：需要返回给前台的数据,可以是字符串或数组   ,return_list =True json数组， return_list =False  json字符串
    | ##@返回值：json
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    t1 = time.time()
    lists = []
    print type(list_or_dict)

    if isinstance(list_or_dict, list) is True:
        dic = {}
        ListOrDict_new = []
        dic['success'] = unicode(str(success))
        dic['data'] = list_or_dict
        ListOrDict_new.append(dic)
        list_or_dict = ListOrDict_new

    if isinstance(list_or_dict, basestring) is True or isinstance(list_or_dict, dict) is True:
        dic = {}
        lists = []
        lists.append(list_or_dict)
        ListOrDict_new = []
        dic['success'] = unicode(str(success))
        dic['data'] = lists
        ListOrDict_new.append(dic)
        list_or_dict = ListOrDict_new

    jsondump = json.dumps(list_or_dict, indent=indent, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(jsondump, content_type="application/json;charset=utf-8")


def http_response_list_json(list_or_dict, success=False, return_list=True, indent=0):
    """
    | ##@函数目的: 返回数据到前台 (作废，不建议继续试用)
    | ##@参数说明：需要返回给前台的数据,可以是字符串或数组   ,return_list =True json数组， return_list =False  json字符串
    | ##@返回值：json
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    t1 = time.time()
    lists = []
    print type(list_or_dict)
    if isinstance(list_or_dict, dict) is True:
        list_or_dict['success'] = unicode(str(success))

        lists.append(list_or_dict)

        list_or_dict = lists

    if isinstance(list_or_dict, list) is True:
        dic = {}
        dic['success'] = unicode(str(success))
        list_or_dict.append(dic)

    if isinstance(list_or_dict, basestring) is True:
        dic = {}
        dic['msg'] = list_or_dict
        dic['success'] = unicode(str(success))
        if return_list is True:
            lists.append(dic)
            list_or_dict = lists
        else:
            list_or_dict = dic

    jsondump = json.dumps(list_or_dict, indent=indent, cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(jsondump, content_type="application/json;charset=utf-8")
    # --------------------------------------------------------------------------------------------------------------
    # 不推荐使用
    # --------------------------------------------------------------------------------------------------------------
