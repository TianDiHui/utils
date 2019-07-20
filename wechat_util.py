# -*- coding: utf-8 -*-
'''
@author: lanxiong lanxiong@cenboomh.com
@file: wechat_util.py
@time: 2018/8/8 8:58
@desc:
'''
import urllib2
import json
import sys
import simplejson

reload(sys)
sys.setdefaultencoding('utf8')


def get_token(corpid, corpsecret):
    gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
    res = urllib2.urlopen(gettoken_url).read().decode('utf-8')
    token_json = json.loads(res)
    token = token_json['access_token']
    return token


def send_data(subject, content, **wechat_config):
    corpid = wechat_config["corpid"]
    corpsecret = wechat_config["corpsecret"]
    agentid = wechat_config["agentid"]
    access_token = get_token(corpid, corpsecret)
    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token

    if wechat_config["touser"] is not None and wechat_config["toparty"] is None:
        send_values = {
            "touser": wechat_config["touser"],
            "msgtype": "text",
            "agentid": agentid,
            "text": {
                "content": subject + '\n' + content
            },
            "safe": "0"
        }

    if wechat_config["toparty"] is not None and wechat_config["touser"] is None:
        send_values = {
            "toparty": wechat_config["toparty"],
            "msgtype": "text",
            "agentid": agentid,
            "text": {
                "content": subject + '\n' + content
            },
            "safe": "0"
        }

    if wechat_config["toparty"] is not None and wechat_config["touser"] is not None:
        send_values = {
            "touser": wechat_config["touser"],
            "toparty": wechat_config["toparty"],
            "msgtype": "text",
            "agentid": agentid,
            "text": {
                "content": subject + '\n' + content
            },
            "safe": "0"
        }

    send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
    send_request = urllib2.Request(send_url, send_data)
    response = urllib2.urlopen(send_request)
    return response


if __name__ == '__main__':
    # subject = str(sys.argv[1])
    # content = str(sys.argv[2])
    corp_id = 'wwb5706e156ad84af7'
    corp_secret = 'EzNYQMrPhYHTibpt235VnFcNyEyKdZtK3wlNLOBm_ps'
    # accesstoken = gettoken(corpid, corpsecret)
    send_data(corp_id, corp_secret, '1000011', 'test_subject', 'test content你好啊')
