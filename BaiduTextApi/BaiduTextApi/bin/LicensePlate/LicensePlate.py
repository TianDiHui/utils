#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/2/19 14:10
# @User    : zhunishengrikuaile
# @File    : LicensePlate.py
# @Email   : binary@shujian.org
# @MyBlog  : WWW.SHUJIAN.ORG
# @NetName : 書劍
# @Software: 百度识图Api封装
# LicensePlate
# 车牌号识别
import os
import base64
import requests
from BaiduTextApi.bin.AccessToken.AccessToken import AccessToken
from BaiduTextApi.config.config import LOCALHOST_PATH, URL_LIST_URL

ACCESS_TOKEN = AccessToken().getToken()['access_token']

LICENSE_PLATE_URL = URL_LIST_URL['LICENSE_PLATE'] + '?access_token={}'.format(ACCESS_TOKEN)


class LicensePlateSuper(object):
    pass


class LicensePlate(LicensePlateSuper):

    def __init__(self, image=None, multi_detect=True):
        self.HEADER = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.IMAGE_CONFIG = {
            'multi_detect': multi_detect,
        }

        if image is not None:
            imagepath = os.path.exists(LOCALHOST_PATH['PATH'] + image)
            if imagepath == True:
                images = LOCALHOST_PATH['PATH'] + image
                with open(images, 'rb') as images:
                    self.IMAGE_CONFIG['image'] = base64.b64encode(images.read())

    def postLicensePlate(self):
        if self.IMAGE_CONFIG.get('image', None) == None:
            return 'image参数不能为空！'
        licensePlate = requests.post(url=LICENSE_PLATE_URL, headers=self.HEADER,
                                     data=self.IMAGE_CONFIG)
        return licensePlate.json()
