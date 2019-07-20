# -*- coding: utf-8 -*-
# 参考:http://www.cnblogs.com/dkblog/archive/2011/08/26/2155018.html
# http://www.cnblogs.com/starof/p/4702026.html
# | ##@函数目的: 日志模块配置
# | ##@参数说明：
# | ##@返回值：
# | ##@函数逻辑：
# | ##@开发人：jhuang
# | ##@时间：
# """
# debug:debug级输出
# info：info 级输出，重要信息
# warning：warning级输出，与warn相同，警告信息
# error：error级输出，错误信息
# critical ：critical级输出，严重错误信息
# 五个等级从低到高分别是debug到critical
# 当seLevel设置为INFO时，可以截获取所有等级的输出


import logging
# 第一步，创建一个logger
import os
from logging.handlers import RotatingFileHandler

logger = None

"""
初始化日志配置

:param param1: this is a first param
:param param2: this is a second param
:returns: this is a description of what is returned
:raises keyError: raises an exception
@author： jhuang
@time：28/04/2018
"""


class Logger():
    def __init__(self,log_handle='default'):
        self.log_handle=log_handle
        pass

    def init(self):

        logger = logging.getLogger(self.log_handle)
        return logger
        # log.error()
    #     self.logger = logging.getLogger(log_name)
    #     self.logger.setLevel(level=logging.DEBUG)
    #     # 定义一个RotatingFileHandler，最多备份3个日志文件，每个日志文件最大1K
    #     # project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #     if os.environ.has_key('log_home'):
    #         project_dir_log = os.path.join(os.environ['log_home'])
    #     else:
    #         project_dir_log = './logs'
    #     if not os.path.exists(project_dir_log):
    #         os.makedirs(project_dir_log)
    #     pid = os.getpid()
    #     rHandler = RotatingFileHandler(os.path.join(project_dir_log, '%s.log' % (log_name)),
    #                                    maxBytes=50 * 1024 * 1024,
    #                                    backupCount=5)
    #     rHandler.setLevel(logging.DEBUG)
    #
    #     logging_filter = logging.Filter()
    #     logging_filter.filter =request_id.logging.RequestIdFilter
    #     rHandler.addFilter(logging_filter)
    #
    #     formatter = logging.Formatter(
    #         '%(asctime)s [request_id:%(request_id)s] [pid:%(process)s] [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s')
    #     rHandler.setFormatter(formatter)
    #
    #     console = logging.StreamHandler()
    #     console.setLevel(logging.DEBUG)
    #     console.setFormatter(formatter)
    #     console.addFilter(logging_filter)
    #
    #     self.logger.addHandler(rHandler)
    #     self.logger.addHandler(console)
    #
    # def info(self, msg):
    #     if self.logger is not None:
    #         self.logger.info(msg)
    #
    # def error(self, msg):
    #     if self.logger is not None:
    #         self.logger.error(msg)
    #
    # def warning(self, msg):
    #     if self.logger is not None:
    #         self.logger.warning(msg)
    #
    # def critical(self, msg):
    #     if self.logger is not None:
    #         self.logger.critical(msg)
    #
    # def debug(self, msg):
    #     if self.logger is not None:
    #         self.logger.debug(msg)
    #
    # def exception(self, msg):
    #     if self.logger is not None:
    #         self.logger.exception(msg)


logger = Logger().init()


# 日志
# logger.debug('this is a logger debug message')
# logger.info('this is a logger info message')
# logger.warning('this is a logger warning message')
# logger.error('this is a logger error message')
# logger.critical('this is a logger critical message')


