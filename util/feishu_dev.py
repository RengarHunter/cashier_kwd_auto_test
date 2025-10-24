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
    # feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/3e58660d-406e-4143-97e7-90bf73230769'
    # secret = '1fji4e9A2VkbqQdKPY1aNb'
    feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/18f1fdbf-82fc-4a71-8b86-01993167c0af'
    secret = '2lBzf9JGZgcsKrycPTpbnb'
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

    def sendTextmessage(self, message):
        url = self.feishu_webhook
        headers = {
            "Content_Type": "application/json; charset=utf-8",
        }
        payload_message = {
            "timestamp": f"{self.timestamp}",
            "sign": f"{self.gen_sign(self.timestamp, self.secret)}",
            "msg_type": "text",
            "content": {
                # "text": f"{message}" + "<at user_id=\"all\">所有人</at>"
                "text": f"{message}"
            }
        }
        response = requests.post(url=url, data=json.dumps(payload_message), headers=headers)
        return response.json()


fsdev = FeiShuTalk()
