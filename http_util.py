# -*- coding: utf-8 -*-
'''
保持一个http session，比如post登录后，可以后续进行需要授权（登录）的操作 
'''
import logging
import time
import urllib
from time import sleep

import requests
# import urllib2
from retrying import retry

from utils.common_util import get_except
from .file_util import get_file_size

logger = logging.getLogger('django')
from .string_util import covert_bytes


class HttpClass():
    def __init__(self, user='', pwd='', headers='', timeout=15, verify=False):
        """
        | ##@函数目的: HTTP 初始化
        | ##@参数说明： 
        | ##@返回值：HTTP 句柄
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        self.session = requests.session()
        self.headers = headers
        if user != '':
            self.session.auth = (user, pwd)
        if self.headers == '':
            self.headers = {
                # "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            }
        self.timeout = timeout
        self.verify = verify

    def urlencode(self, params):
        """
        将字典里面所有的键值转化为query-string格式

        :param params: data = {
            'word': wd,
            'tn': '71069079_1_hao_pg',
            'ie': 'utf-8'
        }
        :param param2: this is a second param
        :returns: string, key=value&key=value
        :raises keyError: raises an exception
        @author： jhuang
        @time：7/16/2019
        """
        query_string = urllib.parse.urlencode(params)
        return query_string

    def close(self):
        '''
        关闭连接
        '''
        self.session.close()

    #         logger.info ('关闭连接')

    def __del__(self):
        self.close()

    def post(self, url, payload):
        """
        | ##@函数目的: post
        | ##@参数说明： 
        payload = {
           'os_username': 'jhuang', 
           'os_password': 'debug.', 
           'os_destination':'',
           'atl_token':'',
           'login':'%E7%99%BB%E5%BD%95'
         }
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """

        logger.debug(payload)
        r = self.session.post(url, data=payload, headers=self.headers, timeout=self.timeout, verify=self.verify)
        return (r, r.text.encode('utf8'))

    def get(self, url):
        """
        | ##@函数目的: HTTP get
        | ##@参数说明： 
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """

        start_time = time.time()
        r = self.session.get(url, headers=self.headers, timeout=self.timeout, verify=self.verify)
        respone_time = time.time() - start_time
        return (r, r.text.encode('utf8'), respone_time)

    @retry(stop_max_attempt_number=20, wait_fixed=6)
    def get_web_status(self, url):
        """
        | ##@函数目的: 检查web是否可以访问
        | ##@参数说明：
        | ##@返回值：返回HTTPcode 无论是多少都任务是web服务可以访问
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        try:
            r = self.session.get(url, stream=True, headers=self.headers, timeout=self.timeout, verify=self.verify)
            status_code = str(r.status_code)
        except Exception as e:
            status_code = ''
        return str(status_code)

    def status_code(self, url):
        """
        | ##@函数目的: 状态码
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        status_code = ''
        try:
            r = self.session.get(url, stream=True, headers=self.headers, timeout=self.timeout, verify=self.verify)
            status_code = str(r.status_code)
        except Exception as e:
            status_code = get_except(e, False, write_log=False)
            # status_code = get_except(e, False)
        return str(status_code)

    def get_remote_file_size(self, url):
        """
        | ##@函数目的: 获取远程文件大小
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """

        RemoteFileSize = 0
        try:
            r = self.session.get(url, stream=True, headers=self.headers, timeout=self.timeout, verify=self.verify)
            RemoteFileSize = int(r.headers['content-length'])
        except:
            RemoteFileSize = -1
        return RemoteFileSize

    def get_download_info(self, url, local_file):
        """
        |##desc: 获取下载信息
        |##:param: None
        |##:return: None
        |##@author： jhuang
        |##@time：2017-07-22
        """
        RemoteFileSize = self.get_remote_file_size(url)
        print
        RemoteFileSize
        if RemoteFileSize == 0: return False
        get_file_size1 = get_file_size(local_file)
        print
        get_file_size1
        sleep(1)
        get_file_size2 = get_file_size(local_file)
        print
        int(get_file_size2), int(get_file_size1)
        speed = covert_bytes(int(get_file_size2) - int(get_file_size1)) + '/s'
        percent = int(get_file_size2) * 100 / int(RemoteFileSize)
        complete = False
        logger.debug('监控到正在下载...远程文件大小：%s,本地文件大小:%s' % (RemoteFileSize, get_file_size2))
        if get_file_size2 >= RemoteFileSize or percent >= 99:
            logger.debug('监控到下载完成！远程文件大小：%s,本地文件大小:%s' % (RemoteFileSize, get_file_size2))
            complete = True
        return (RemoteFileSize, percent, speed, complete)

    def download(self, url, file_path, timeout=60 * 30):
        """
        | ##@函数目的: HTTP get
        | ##@参数说明： 
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        time_start = time.time()
        logger.debug('%s -> %s' % (url, file_path))

        r = self.session.get(url, stream=True, timeout=timeout, headers=self.headers, verify=self.verify)
        f = open(file_path, "wb")
        logger.debug(r.status_code)
        if r.status_code != 404 and r.status_code != 401:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
            logger.debug('下载文件成功!-> %s ' % (url))
            f.close()
        elif r.status_code == 401:
            logger.debug('下载文件失败,状态码:%s' % (r.status_code))
        else:
            logger.debug('下载文件失败,状态码:%s' % (r.status_code))
        logger.debug('下载文件用时：%s' % (time.time() - time_start))
        return (r, file_path)


def http_get_utf8(url):
    """
    | ##@函数目的: get,解决乱码问题
    | ##@参数说明：HTTP地址
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    ohttp = HttpClass()
    ret = ohttp.get(url)
    ohttp.close()
    return ret[1]


def http_statu_code(url):
    """
    | ##@函数目的: 获取HTTP状态码 (注意这个是没带SESSION)
    | ##@参数说明：HTTP地址
    | ##@返回值：字符型HTTP状态码
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    if url == None or url == '':
        return 'null'
    ohttp = HttpClass(timeout=5)
    status_code = ohttp.status_code(url)
    ohttp.close()

    return status_code


# def http_get_basic_auth(url, username, password):
#     """
#     |##desc: HTTP基础认证
#     |##:param: None
#     |##:return: None
#     |##@author： jhuang
#     |##@time：8/31/2017
#     """
#
#     try:
#         # 创建一个密码管理者
#         password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
#         # 添加用户名和密码
#         password_mgr.add_password(None, url, username, password)
#         # 创建了一个新的handler
#         handler = urllib2.HTTPBasicAuthHandler(password_mgr)
#         # 创建 "opener"
#         opener = urllib2.build_opener(handler)
#         # 使用 opener 获取一个URL
#         opener.open(url)
#         # 安装 opener.
#         urllib2.install_opener(opener)
#         # urllib2.urlopen 使用上面的opener.
#         ret = urllib2.urlopen(url)
#         return ret.read()
#     except Exception as  e:
#         if e.code == 401:
#             return "authorization failed"
#         else:
#             raise e
#     except:
#         return None
