# -*- coding: utf-8 -*-
import threading

import threadpool

logger = logging.getLogger('django')


# 参考文档：http://blog.csdn.net/hehe123456zxc/article/details/52258431

class ThreadPool(object):

    def __init__(self, max_thread):
        logger.debug('初始化池，线程数：%s' % (max_thread))
        self.pool = threadpool.ThreadPool(max_thread)
        self.poolsize = max_thread

    def start(self, func, param_list, wait=True):
        """
        |##@函数目的：开始线程池并控制同时线程数
        |##@参数说明：
        func 需要执行的函数
        param_list list 类型 
            参数示例 :
            lists=[]
            for obj in data:
                dic={}
                dic['warfilename']= str(obj[1])
                dic['dep_task_id']=str(obj[0])
                arrays=(None, dic)
                lists.append(arrays)   
            logger.info  ( lists
        maxThread=同时最大线程数
        |##@返回值：
        |##@函数逻辑：
        |##@开发人：jhuang
        |##@时间：
        """
        if len(param_list) == 0:
            logger.debug('提交到线程池的任务为空！')
            return False

        reqs = threadpool.makeRequests(func, param_list)
        [self.pool.putRequest(req) for req in reqs]
        if wait:
            logger.debug('等待线程池内任务完成...')
            self.pool.wait()
            logger.debug('线程池内任务完成！')

        # logger.debug('线程池内任务完成!回收线程！')
        # self.stop()
        return True

    # def stop(self):
    #     if self.pool.dismissedWorkers:
    #         self.pool.joinAllDismissedWorkers()


def get_thread_name():
    """
    | ##@函数目的: 获取当前线程
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    threadname = threading.current_thread().getName()
    # 线程索引
    # thread_name = threading.current_thread().ident
    # logger.info  ( 'threadname->' +threadname
    return threadname
