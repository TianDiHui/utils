#!/usr/bin/env python
# -*- encoding: utf-8 -*-


# 官方文档：https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.AYkd7q&treeId=257&articleId=105735&docType=1

import json

from http_util import HttpClass


class DingtalkRobot(object):
    """
    钉钉机器人类

    :param param1: this is a first param
    :param param2: this is a second param
    :returns: this is a description of what is returned
    :raises keyError: raises an exception
    @author： jhuang
    @time：02/04/2018
    """

    def __init__(self, access_token):
        self.access_token = access_token
        self.send_api = 'https://oapi.dingtalk.com/robot/send'
        self.ohttp = HttpClass(headers={"Content-Type": "application/json"})

    def send_text_msg(self, text):
        """
        钉钉机器人发送消息

        :param param1: this is a first param
        :param param2: this is a second param
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        @author： jhuang
        @time：02/04/2018
        """
        jsons = {"msgtype": "text", "text": {"content": text}}
        jsons = json.dumps(jsons)
        ret = self.ohttp.post('%s?access_token=%s' % (self.send_api, self.access_token), payload=jsons)
        api_ret_json = json.loads(ret[1])
        if int(api_ret_json['errcode']) > 0:
            raise Exception('接口返回错误：%s' % ret[1])
        return ret

    def send_link_msg(self, title, text, picUrl, messageUrl):
        jsons = {"msgtype": "link",
                 "link": {"text": text,
                          "title": title,
                          "picUrl": picUrl,
                          "messageUrl": messageUrl
                          }
                 }
        jsons = json.dumps(jsons)
        ret = self.ohttp.post('%s?access_token=%s' % (self.send_api, self.access_token), payload=jsons)
        api_ret_json = json.loads(ret[1])
        if int(api_ret_json['errcode']) > 0:
            raise Exception('接口返回错误：%s' % ret[1])
        return ret

#
# dr = DingtalkRobot('668c5686338a576f1b38301839c2b10a6be2a218b2e74be8df4b013439d72878')
# dr.send_link_msg('QQ机器人扫码通知', '连云港机器人可能需要扫码！', 'https://srmc.cenboomh.com/static/images/robot_qcode_default.png',
#                  'https://srmc.cenboomh.com/static/templates/chat_robot/index.html')
