#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/2/15 15:23
# @User    : zhunishengrikuaile
# @File    : BankCard.py
# @Email   : binary@shujian.org
# @MyBlog  : WWW.SHUJIAN.ORG
# @NetName : 書劍
# @Software: 百度识图Api封装
# 银行卡识别
import os
import base64
import requests
from BaiduTextApi.bin.AccessToken.AccessToken import AccessToken
from BaiduTextApi.config.config import LOCALHOST_PATH, URL_LIST_URL

ACCESS_TOKEN = AccessToken().getToken()['access_token']
BANK_CARD_URL = URL_LIST_URL['BANK_CARD'] + '?access_token={}'.format(ACCESS_TOKEN)


class BankCardSuper(object):
    pass


class BankCard(BankCardSuper):
    def __init__(self, image=None):
        self.HEADER = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.IMAGE_CONFIG = {
            'image': None
        }

        if image is not None:
            imagepath = os.path.exists(LOCALHOST_PATH['PATH'] + image)
            if imagepath == True:
                images = LOCALHOST_PATH['PATH'] + image
                with open(images, 'rb') as images:
                    self.IMAGE_CONFIG['image'] = base64.b64encode(images.read())

    def postBankCard(self):
        if self.IMAGE_CONFIG.get('image', None) == None:
            return 'image参数不能为空！'
        bankCard = requests.post(url=BANK_CARD_URL, headers=self.HEADER, data=self.IMAGE_CONFIG)
        return bankCard.json()
