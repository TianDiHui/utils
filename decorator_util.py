# -*- coding: utf-8 -*-
import functools
import threading

# 装饰器模块
import time

from common_util import response_json

from utils.common_util import get_except
logger = logging.getLogger('django')


def myasync(func):
    """
        实现函数异步执行
        :param param1: this is a first param
        :param param2: this is a second param
        :returns: 返回json格式的异常到前台
        :raises keyError: raises an exception
        @author： jhuang
        @time：08/02/2018
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        my_thread.start()

    return wrapper


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

                ret= func(*args, **kwargs)
                # logger.debug('函数(%s)用时：%s' % (__name__,time.time() - start_time))
                print '函数(%s)用时(s)：%s' % (func.__name__,time.time() - start_time)

                return ret
            except Exception as e:
                # pass
                logger.exception('view_except')

                return response_json(get_except(e), error_code=error_code)

                # re-raise the exception
                raise

        return inner_wrapper

    return wrapper