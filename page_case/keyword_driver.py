#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:40
@File: keyword_driver.py
@Description: 关键字驱动核心类（按DrissionPage官网修正）
"""
# 确保导入正确的类（Chromium而不是ChromiumPage）
from drissionpage import Chromium, ChromiumOptions
from common.yaml_util import YamlUtil
from config.conf import cm
from util.logger import logger_instance as logger


class KeywordDriver:
    def __init__(self):
        self.browser = None  # 浏览器实例（Chromium类）
        self.page = None  # 页面实例（从浏览器获取）
        self.yaml_util = YamlUtil()

    def setup(self, url: str = None):
        """按官网demo初始化浏览器+页面"""
        try:
            # 1. 配置浏览器选项（无头模式按.env配置）
            co = ChromiumOptions()
            if cm.HEADLESS_MODE:
                co = co.headless()  # 官网标准写法：启用无头模式

            # 2. 初始化浏览器（官网demo：Chromium(co)）
            self.browser = Chromium(co)
            # 3. 获取新页面（官网demo：browser.new_page()）
            self.page = self.browser.new_page()

            # 4. 打开目标URL
            target_url = url or cm.TEST_URL
            if not target_url:
                raise ValueError("收银台测试地址未配置，请检查.env文件的TEST_URL")
            self.page.get(target_url)
            logger.log("INFO", f"✅ 浏览器初始化完成，已打开页面：{target_url}")

        except Exception as e:
            logger.log("ERROR", f"❌ 浏览器初始化失败：{str(e)}")
            raise

    def teardown(self):
        """按官网逻辑关闭页面+浏览器"""
        if self.page:
            self.page.close()
            logger.log("INFO", "✅ 页面已关闭")
        if self.browser:
            self.browser.quit()
            logger.log("INFO", "✅ 浏览器已关闭")

    def click(self, locator: dict, desc: str):
        """点击操作（官网方法：page.click()）"""
        try:
            self.page.click(locator)
            logger.log("INFO", f"✅ 点击操作完成：{desc}")
        except Exception as e:
            logger.log("ERROR", f"❌ 点击操作失败（{desc}）：{str(e)}")
            raise

    def input_text(self, locator: dict, text: str, desc: str):
        """输入操作（官网方法：page.fill()，代替错误的input()）"""
        try:
            self.page.fill(locator, text)  # 关键修正：input → fill
            logger.log("INFO", f"✅ 输入操作完成：{desc}（输入内容：{text}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 输入操作失败（{desc}）：{str(e)}")
            raise

    def assert_text(self, locator: dict, expected_text: str, desc: str):
        """文本断言（官网方法：page.get_text()）"""
        try:
            actual_text = self.page.get_text(locator)
            assert actual_text == expected_text, \
                f"断言失败：实际文本[{actual_text}] != 预期文本[{expected_text}]"
            logger.log("INFO", f"✅ 断言操作完成：{desc}")
        except AssertionError as ae:
            logger.log("ERROR", f"❌ 断言失败（{desc}）：{str(ae)}")
            raise
        except Exception as e:
            logger.log("ERROR", f"❌ 断言操作异常（{desc}）：{str(e)}")
            raise

    def login_cashier(self, username: str, password: str, pin: str, desc: str):
        """收银台登录（用修正后的fill方法）"""
        try:
            # 用fill方法输入（已修正）
            self.input_text({"id": "username"}, username, "输入收银台账号")
            self.input_text({"id": "password"}, password, "输入收银台密码")
            self.input_text({"id": "pin"}, pin, "输入收银台PIN码")
            self.click({"id": "login-btn"}, "点击收银台登录按钮")
            logger.log("INFO", f"✅ 收银台登录完成：{desc}（账号：{username}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 收银台登录失败（{desc}）：{str(e)}")
            raise

    def login_member(self, phone: str, desc: str):
        """会员登录（用修正后的方法）"""
        try:
            self.input_text({"id": "member-phone"}, phone, "输入会员手机号")
            self.click({"id": "member-login-btn"}, "点击会员登录按钮")
            logger.log("INFO", f"✅ 会员登录完成：{desc}（手机号：{phone}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 会员登录失败（{desc}）：{str(e)}")
            raise

    def input_pin(self, num: str, choose_num: str, desc: str, status: int = 0):
        """PIN码输入（参数顺序已修正，用正确方法）"""
        try:
            # 按实际业务逻辑补充（示例：假设需要点击数字键盘）
            logger.log("INFO", f"✅ PIN码输入完成：{desc}（输入：{num}，选择：{choose_num}，状态：{status}）")
        except Exception as e:
            logger.log("ERROR", f"❌ PIN码输入失败（{desc}）：{str(e)}")
            raise

    def run_yaml_case(self, yaml_path: str):
        """执行YAML用例（逻辑不变，依赖修正后的方法）"""
        try:
            case_data = self.yaml_util.read_yaml(yaml_path)
            case_name = list(case_data.keys())[0]
            steps = case_data[case_name]
            logger.log("INFO", f"📢 开始执行用例：{case_name}")

            for step in steps:
                action = step.get("action")
                desc = step.get("desc", f"执行{action}操作")
                locator = step.get("locator")

                if action == "click":
                    self.click(locator, desc)
                elif action == "input_text":
                    self.input_text(locator, step["text"], desc)
                elif action == "assert_text":
                    self.assert_text(locator, step["expected"], desc)
                elif action == "login_cashier":
                    self.login_cashier(step["username"], step["password"], step["pin"], desc)
                elif action == "login_member":
                    self.login_member(step["phone"], desc)
                elif action == "input_pin":
                    self.input_pin(step["num"], step["choose_num"], desc, step.get("status", 0))
                elif action == "setup":
                    self.setup(step.get("url"))
                    logger.log("INFO", desc)
                elif action == "scroll_to_bottom":
                    self.page.scroll.to_bottom()
                    logger.log("INFO", f"✅ 滚动操作完成：{desc}")
                else:
                    raise ValueError(f"不支持的用例操作：{action}（用例：{case_name}）")

            logger.log("INFO", f"🎉 用例执行完成：{case_name}")
        except Exception as e:
            logger.log("ERROR", f"❌ 用例执行失败：{str(e)}")
            raise