#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 11:05
@File: utils.py.py
@Description: 
"""


from DrissionPage import WebPage
from util.logger import Logger
from util.times import sleep

logger = Logger()

def click_pin(page: WebPage, num: str, choose_num: int, status=0):
    """收银台PIN码输入（DrissionPage版本）"""
    dict_cash = {
        '1': f'(//div[@class="el-col el-col-18"]/div[1]/div[1]/div[1])[{choose_num}]',
        '2': f'(//div[@class="el-col el-col-18"]/div[1]/div[2]/div[1])[{choose_num}]',
        '3': f'(//div[@class="el-col el-col-18"]/div[1]/div[3]/div[1])[{choose_num}]',
        '4': f'(//div[@class="el-col el-col-18"]/div[2]/div[1]/div[1])[{choose_num}]',
        '5': f'(//div[@class="el-col el-col-18"]/div[2]/div[2]/div[1])[{choose_num}]',
        '6': f'(//div[@class="el-col el-col-18"]/div[2]/div[3]/div[1])[{choose_num}]',
        '7': f'(//div[@class="el-col el-col-18"]/div[3]/div[1]/div[1])[{choose_num}]',
        '8': f'(//div[@class="el-col el-col-18"]/div[3]/div[2]/div[1])[{choose_num}]',
        '9': f'(//div[@class="el-col el-col-18"]/div[3]/div[3]/div[1])[{choose_num}]',
    }
    if status == 0:
        dict_cash['0'] = f'(//div[@class="el-col el-col-18"]/div[4]/div[1]/div[1])[{choose_num}]'
    elif status == 1:
        dict_cash['.'] = f'(//div[@class="el-col el-col-18"]/div[4]/div[1]/div[1])[{choose_num}]'
        dict_cash['0'] = f'(//div[@class="el-col el-col-18"]/div[4]/div[2]/div[1])[2]'

    def input_num(key_):
        xpath_ = dict_cash[key_]
        page.ele(xpath=xpath_).click()
        sleep(0.1)

    [input_num(i) for i in num]
    logger.info(f"输入PIN码: {num}")

def remove_modal_overlay(page: WebPage):
    """移除遮罩层（DrissionPage版本）"""
    try:
        page.run_js("""
            var modal = document.querySelector('.v-modal');
            if (modal) modal.parentNode.removeChild(modal);
        """)
        logger.info("移除遮罩层成功")
    except Exception as e:
        logger.error(f"移除遮罩层失败: {str(e)}")

