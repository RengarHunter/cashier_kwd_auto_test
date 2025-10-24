#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@author: Lawrence
@file: send_mail.py
@time: 2023/10/17 10:11
"""
import zmail

from config.conf import cm
from util import times


def send_report():
    time_ = times.dt_strftime("%Y-%m-%d %H:%M:%S")
    """发送报告"""
    # with open(cm.REPORT_FILE, encoding='utf-8') as f:
    #     content_html = f.read()
    try:
        mail = {
            'from': 'xie.long@diplus.com.cn',
            'subject': f'{time_}' + " " * 2 + '自动化测试报告',
            'content_html': 'test',  # content_html,
            'attachments': 'test',  # [cm.REPORT_FILE, ]
        }
        server = zmail.server(*cm.EMAIL_INFO.values())
        server.send_mail(cm.ADDRESSEE, mail)
        msg_ = '自动化测试报告已发送。'
        print(msg_)
    except Exception as e:
        msg_ = "Error: 无法发送邮件，{}".format(e)
        print(msg_)
        # log.info(msg_)


if __name__ == '__main__':
    send_report()
