# -*- coding: utf-8 -*-
import re

logger = logging.getLogger('django')
from utils.common_util import get_except
from http_util import HttpClass


class Confluence(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.ohttp = None
        self.confluence_server_url = None

    def login(self, url, username, password):
        """
        | ##@函数目的: 登录
        | ##@参数说明：
        | ##@返回值：登录句柄
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        self.confluence_server_url = url
        data = {'login': '%E7%99%BB%E5%BD%95',
                'os_username': username,
                'os_password': password,
                'os_destination': '',
                'atl_token': type
                }
        #         if self.ohttp ==None:
        self.ohttp = HttpClass()
        logger.debug('登录Confluence...')
        ret, html = self.ohttp.post(self.confluence_server_url + '/login.jsp', data)
        #         else:
        #             logger.info  ( u'已登录Confluence,无需登录!')
        # logger.info  ( html)
        return self.ohttp

    def logout(self):
        self.ohttp.get('%s/logout.action' % (self.confluence_server_url))
        self.ohttp.close()

    def get_avatar(self, username):
        """
        | ##@函数目的: 获取用户头像
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        ret, html,respone_time = self.ohttp.get(
            self.confluence_server_url + '/rest/spacedirectory/1/search?label=~' + username + '%3Afavourite&label=~' + username + '%3Afavorite&_=1483072547386')
        try:
            R = re.findall('"image/png" href="(http.*?(?:jpg|png))', html)
            if len(R) > 1:
                return R[1]
            else:
                return None
        except Exception as e:
            get_except(e)
            return None

    def get_page_title(self, pageid):
        """
        | ##@函数目的: 获取文档标题
        | ##@参数说明：
        | ##@返回值：
        | ##@函数逻辑：
        | ##@开发人：jhuang
        | ##@时间：
        """
        ret, html = self.ohttp.get('%s/pages/viewpage.action?pageId=%s' % (self.confluence_server_url, pageid))
        r = re.findall('<meta name="ajs-page-title" content="(.*?)">', html, re.M)
        if len(r) > 0:
            return r[0]
        else:
            return None
