#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 11:06
@File: conftest.py
@Description: 
"""

import pytest
from common.data_init import CashierDataInit
from page_case.keyword_driver import KeywordDriver
from config.conf import cm
from util.logger import logger_instance  # 导入你的日志实例

# 日志别名（使用你的Logger单例）
logger = logger_instance
data_init = CashierDataInit()


# 全局数据初始化Fixture
@pytest.fixture(scope="session", autouse=True)
def init_test_data():
    """全局数据初始化（所有用例执行前运行1次）"""
    # 替换 logger.info 为 logger.log("INFO", ...)
    logger.log("INFO", "=" * 50)
    logger.log("INFO", "开始全局数据初始化：清空订单、发送优惠券、初始化会员数据")
    data_init.clear_test_data()
    logger.log("INFO", "全局数据初始化完成")
    logger.log("INFO", "=" * 50)
    yield
    logger.log("INFO", "测试完成，执行后置清理")


# 关键字驱动Fixture
@pytest.fixture(scope="function")
def keyword_driver():
    """每个用例创建1个KeywordDriver实例，自动setup/teardown"""
    driver = KeywordDriver()
    yield driver
    driver.teardown()  # 用例结束后自动关闭浏览器
