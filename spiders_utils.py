# -*- coding: utf-8 -*-
import re

import requests
from loguru import logger


class ArticleSpider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        }
        self.proxies = {}

        # 如果代理不稳定，不推荐使用
        # local showdowsocks service
        # proxies example:
        # proxies = {
        #     "http": "socks5://127.0.0.1:1080",
        #     "https": "socks5://127.0.0.1:1080",
        # }

    def get_list(self, target_url, pattern):
        """
        获取文章列表

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：7/29/2019
        """

        logger.info('crawling : %s' % target_url)
        html = requests.get(target_url, headers=self.headers, proxies=self.proxies)
        html.encoding = 'utf-8'  # 这一行是将编码转为utf-8否则中文会显示乱码。
        html = html.text
        html = re.findall(pattern, html.text, re.S)
        title_list = []
        for r in html:
            dict = {}
            dict['title'] = r[0]
            dict['url'] = r[1]
            title_list.append(dict)
        return title_list

    def get_content(self, target_url, pattern):
        """
        获取文章内容

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：7/29/2019
        """
        logger.info('crawling : %s' % target_url)
        html = requests.get(target_url, headers=self.headers, proxies=self.proxies)
        html.encoding = 'utf-8'  # 这一行是将编码转为utf-8否则中文会显示乱码。
        html = html.text
        html = re.findall(pattern, html.text, re.S)[0]
        return html
