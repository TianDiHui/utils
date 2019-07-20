# -*- coding: utf-8 -*-

import threading
import time
import urllib

import wget

logger = logging.getLogger('django')


def wget_download(url, file_path):
    """
    | ##@函数目的: 下载远程文件 带进度条
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    logger.debug('wget_download :' + url + ', to:' + file_path)
    wget.download(url, file_path)


def download_file(url, file_path):
    """
    | ##@函数目的: 下载远程文件
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    url = str(url).replace(' ', '')
    file_path = str(file_path).replace(' ', '')
    logger.debug('download_file : %s to %s ' % (url, file_path))
    start = time.clock()
    urllib.urlretrieve(url, file_path, download_file_callback)
    logger.debug('下载(%s->%s)完成,用时:%s' % (url, file_path, time.clock() - start))


def download_file_callback(a, b, c):
    '''''
    下载文件回调
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
   '''
    #     return True
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    # logger.info  ( str(int(per))
    if str(int(per))[1:2] == "0":
        logger.debug('%.2f%%' % per)


class downloader(threading.Thread):
    """
    | ##@函数目的:  多线程下载类 用于多线程同时下载多个文件
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    def __init__(self, url, name):
        threading.Thread.__init__(self)
        self.url = url
        self.name = name

    def run(self):
        logger.debug('downloading from %s' % self.url)
        urllib.urlretrieve(self.url, self.name)


def download_multi(arrays):
    """
    | ##@函数目的:  多线程同时下载多个文件
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    #调用实例
    # dic={}
    # arrays=[]
    # dic['url']='http://f.hiphotos.baidu.com/image/h%3D200/sign=d1233ebf3ca85edfe58cf923795509d8/0ff41bd5ad6eddc43cc8e31431dbb6fd52663335.jpg'
    # dic['file']='e:\\0ff41bd5ad6eddc43cc8e31431dbb6fd52663335.jpg'
    # arrays.append(dic)
    # dic={}
    # dic['url']='http://desk.fd.zol-img.com.cn/t_s960x600c5/g5/M00/08/00/ChMkJlexsMuIQie-AAg2b09O224AAUdPgM-mJwACDaH277.jpg'
    # dic['file']='e:\\0mJwACDaH277.jpg'
    # arrays.append(dic)
    # #logger.info  ( arrays
    # 
    # download_multi(arrays)
    """
    threads = []
    for a in arrays:
        url = a['url']
        file_path = a['file']
        logger.debug('downlowning start ....url=', url, '，file=', file_path)
        t = downloader(url, file)
        threads.append(t)
        t.start()
    # 等待主线程完成
    for t in threads:
        t.join()
