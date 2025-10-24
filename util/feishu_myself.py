#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@author: Lawrence
@file: feishu_dev.py
@time: 2023/10/23 17:41
"""
import base64
import hashlib
import hmac
import json
import time

import requests


class FeiShuTalk:
    feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/f1cc555d-a514-492f-9f8b-c5cda2c35756'
    secret = 'T4hhaJGRRMkVFin5JhgaKc'
    timestamp = time.time()
    timestamp = str(timestamp).split('.')[0]

    # print(timestamp)

    @staticmethod
    def gen_sign(timestamp, secret):
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def sendTextmessage(self, message, status=1):
        url = self.feishu_webhook
        headers = {
            "Content_Type": "application/json; charset=utf-8",
        }
        if status == 1:
            payload_message = {
                "timestamp": f"{self.timestamp}",
                "sign": f"{self.gen_sign(self.timestamp, self.secret)}",
                "msg_type": "text",
                "content": {
                    # "text": f"{message}" + "<at user_id=\"all\">所有人</at>"
                    "text": "{}".format(message)
                }
            }
            response = requests.post(url=url, data=json.dumps(payload_message), headers=headers)
            return response.json()
        else:
            payload_message = {
                "timestamp": f"{self.timestamp}",
                "sign": f"{self.gen_sign(self.timestamp, self.secret)}",
                "msg_type": "text",
                "content": {
                    "text": f"{message}" + "<at user_id=\"all\">所有人</at>"
                    # "text": "{}".format(message)
                }
            }
            response = requests.post(url=url, data=json.dumps(payload_message), headers=headers)
            return response.json()


fsm = FeiShuTalk()
