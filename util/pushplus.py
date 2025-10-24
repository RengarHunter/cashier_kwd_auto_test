#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@author: Lawrence
@file: a.py
@time: 2023/11/13 16:49
"""
import requests


def send_group_message(title, content):
    """
    微信推送模块
    """
    url = 'http://www.pushplus.plus/send'
    headers = {"Content-Type": 'application/json'}
    data = {
        "token": 'a222a03fa2934da9bffcfa422df9fd7e',
        "topic": 'report',
        "title": title,
        "template": "markdown",
        "content": content
    }
    # 发送请求
    r = requests.post(url, headers=headers, json=data)
    print(r.text)
