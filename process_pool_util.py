# -*- coding: utf-8 -*-


import multiprocessing
import time

logger = logging.getLogger('django')


class ProcessPool(object):
    """
    进程池

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：26/06/2018
    """

    def __init__(self, max_process):
        logger.debug('初始化进程池，进程数：%s' % (max_process))
        self.pool = multiprocessing.Pool(processes=max_process)
        self.poolsize = max_process

    def start(self, func, args_list, wait=True):
        # args_list = [(1, 2,), (11, 22)]
        results = []
        e1 = time.time()
        for r in args_list:

            results.append(self.pool.apply_async(func, r))
        self.pool.close()  # 关闭进程池，表示不能在往进程池中添加进程
        if wait:
            logger.debug('等待【进程池】内任务完成...')
            self.pool.join()  # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
            for res in results:
                print (res.get())
            logger.debug('【进程池】内任务完成！用时：%s' % (e1 - time.time()))

        return True
