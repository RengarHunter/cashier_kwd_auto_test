#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:40
@File: conf.py
@Description: 
"""

import os
from dotenv import load_dotenv

import os
from dotenv import load_dotenv
from util.times import dt_strftime


class ConfigManager(object):
    # 单例模式（确保全局只有一个配置实例）
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # 加载.env文件（优先读取项目根目录的.env）
        load_dotenv(os.path.join(self.BASE_DIR, ".env"), override=True)
        self._init_paths()  # 初始化所有路径
        self._init_env_vars()  # 初始化环境变量配置

    # ---------------- 基础路径配置 ----------------
    @property
    def BASE_DIR(self):
        """项目根目录（D:\auto-cashier）"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _init_paths(self):
        """初始化所有目录路径（不存在则自动创建）"""
        # 页面元素YAML目录（page_elements）
        self.ELEMENT_PATH = os.path.join(self.BASE_DIR, "page_elements")
        # 测试用例目录（testcase）
        self.TESTCASE_PATH = os.path.join(self.BASE_DIR, "testcase")
        # 截图目录（screen_capture）
        self.SCREENSHOT_PATH = os.path.join(self.BASE_DIR, "screen_capture")
        # 日志目录（logs）
        self.LOG_PATH = os.path.join(self.BASE_DIR, "logs")
        # JSON数据目录（json）
        self.JSON_PATH = os.path.join(self.BASE_DIR, "json")
        # Allure报告相关目录
        self.ALLURE_RESULTS_PATH = os.path.join(self.BASE_DIR, "allure-results")  # 结果目录
        self.ALLURE_REPORT_PATH = os.path.join(self.BASE_DIR, "allure-report")  # 报告目录

        # 自动创建所有目录（不存在则创建）
        for path in [
            self.ELEMENT_PATH, self.TESTCASE_PATH, self.SCREENSHOT_PATH,
            self.LOG_PATH, self.JSON_PATH, self.ALLURE_RESULTS_PATH, self.ALLURE_REPORT_PATH
        ]:
            if not os.path.exists(path):
                os.makedirs(path)

    # ---------------- 环境变量配置（从.env读取） ----------------
    def _init_env_vars(self):
        """从.env文件读取配置（支持默认值）"""
        # 测试环境URL
        self.TEST_URL = os.getenv("TEST_URL", "https://pos.amfuture.sg/cashier/Login")
        # 浏览器无头模式（True/False）
        self.HEADLESS_MODE = os.getenv("HEADLESS_MODE", "True").lower() == "true"
        # 测试超时时间（秒）
        self.TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "60"))

        # 敏感信息（飞书、账号等）
        self.FEISHU_BOT_TOKEN = os.getenv("FEISHU_BOT_TOKEN", "")
        self.FEISHU_GROUP_ID = os.getenv("FEISHU_GROUP_ID", "")
        self.CASHIER_USER = os.getenv("CASHIER_USER", "James")
        self.CASHIER_PWD = os.getenv("CASHIER_PWD", "sbtccnm123")
        self.CASHIER_PIN = os.getenv("CASHIER_PIN", "6666")
        self.MEMBER_PHONE = os.getenv("MEMBER_PHONE", "24120501")

        # 商家后台配置
        self.SHOP_LOGIN_URL = os.getenv("SHOP_LOGIN_URL", "https://pos.amfuture.sg/index.php/shop/passport/login")
        self.SHOP_USER = os.getenv("SHOP_USER", "自动化测试")
        self.SHOP_PWD = os.getenv("SHOP_PWD", "123456")

        # 用例分组标记（主流程/非主流程）
        self.MAIN_CASE_MARK = os.getenv("MAIN_CASE_MARK", "main")
        self.OTHER_CASE_MARK = os.getenv("OTHER_CASE_MARK", "other")

    # ---------------- 常用路径快捷访问 ----------------
    @property
    def log_file(self):
        """当前日志文件路径（带时间戳，如logs/20251024120000.log）"""
        return os.path.join(self.LOG_PATH, f"{dt_strftime()}.log")

    @property
    def report_file(self):
        """HTML报告路径（report.html）"""
        return os.path.join(self.BASE_DIR, "report.html")

    def json_file(self, filename):
        """生成JSON文件完整路径（如json/report.json）"""
        return os.path.join(self.JSON_PATH, filename)

    # ---------------- 邮件配置（保留你的原有功能） ----------------
    @property
    def EMAIL_INFO(self):
        return {
            'username': 'xie.long@diplus.com.cn',
            'password': 'gZjAG5G50WN8Ynzp',
            'smtp_host': 'smtp.feishu.cn',
            'smtp_port': 465
        }

    @property
    def ADDRESSEE(self):
        return ['xie.long@diplus.com.cn']


# 全局唯一配置实例（所有模块通过该实例访问配置）
cm = ConfigManager()

# 测试代码（验证配置是否正确）
if __name__ == '__main__':
    print(f"项目根目录: {cm.BASE_DIR}")
    print(f"测试URL: {cm.TEST_URL}")
    print(f"日志文件路径: {cm.log_file}")
    print(f"Allure结果目录: {cm.ALLURE_RESULTS_PATH}")
    print(f"主流程用例标记: {cm.MAIN_CASE_MARK}")
    # 运行后检查输出是否符合预期
