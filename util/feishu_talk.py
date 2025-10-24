#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@author: Lawrence
@file: feishu_talk.py
@time: 2023/10/23 16:56
"""
import base64
import hashlib
import hmac
import json
import time

import requests


class FeiShuTalk:
    # feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/847d9266-a79d-41b8-a80c-88ce1f133aa5'
    feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/6fba75b8-dbc4-4d33-bb9f-a594d0248243'
    secret = 'yYH8nG2Em85wjDzyicV0Vd' # 'mm285yjq24tHM76G1ALjBe'
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


fst = FeiShuTalk()
