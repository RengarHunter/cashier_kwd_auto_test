#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:40
@File: keyword_driver.py
@Description: 关键字驱动核心类
"""
from drissionpage import ChromiumPage, ChromiumOptions
from common.yaml_util import YamlUtil
from config.conf import cm
from util.logger import logger_instance as logger


class KeywordDriver:
    def __init__(self):
        self.page = None  # DrissionPage浏览器实例
        self.yaml_util = YamlUtil()  # YAML工具实例

    def setup(self, url: str = None):
        """
        用例前置操作：初始化浏览器、打开测试页面
        :param url: 从YAML传入的页面URL，优先级高于配置的TEST_URL
        """
        try:
            # 1. 配置浏览器选项（按cm中的无头模式配置）
            co = ChromiumOptions()
            if cm.HEADLESS_MODE:
                co.headless(True)  # 启用无头模式（从.env读取配置）

            # 2. 注释掉CHROME_PATH（自动识别系统Chrome路径，无需手动指定）
            # co.set_browser_path(cm.CHROME_PATH)  # 原错误行，已注释

            # 3. 确定目标URL（YAML传的优先，否则用cm.TEST_URL）
            target_url = url or cm.TEST_URL
            if not target_url:
                raise ValueError("收银台测试地址未配置，请检查.env文件的TEST_URL")

            # 4. 初始化浏览器并打开页面
            self.page = ChromiumPage(options=co)
            self.page.get(target_url)
            logger.log("INFO", f"✅ 浏览器初始化完成，已打开页面：{target_url}")

        except Exception as e:
            logger.log("ERROR", f"❌ 浏览器初始化失败：{str(e)}")
            raise  # 抛出异常终止用例

    def teardown(self):
        """用例后置操作：关闭浏览器"""
        if self.page:
            self.page.quit()
            logger.log("INFO", "✅ 浏览器已关闭")

    def click(self, locator: dict, desc: str):
        """点击操作（封装DrissionPage点击）"""
        try:
            self.page.click(locator)
            logger.log("INFO", f"✅ 点击操作完成：{desc}")
        except Exception as e:
            logger.log("ERROR", f"❌ 点击操作失败（{desc}）：{str(e)}")
            raise

    def input_text(self, locator: dict, text: str, desc: str):
        """输入操作（封装DrissionPage输入）"""
        try:
            self.page.input(locator, text)
            logger.log("INFO", f"✅ 输入操作完成：{desc}（输入内容：{text}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 输入操作失败（{desc}）：{str(e)}")
            raise

    def assert_text(self, locator: dict, expected_text: str, desc: str):
        """文本断言（验证元素文本是否符合预期）"""
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
        """收银台登录（组合操作：输入账号→输入密码→输入PIN→点击登录）"""
        try:
            # 假设登录页面元素locator在YAML中定义，此处按实际逻辑补充
            self.input_text({"id": "username"}, username, "输入收银台账号")
            self.input_text({"id": "password"}, password, "输入收银台密码")
            self.input_text({"id": "pin"}, pin, "输入收银台PIN码")
            self.click({"id": "login-btn"}, "点击收银台登录按钮")
            logger.log("INFO", f"✅ 收银台登录完成：{desc}（账号：{username}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 收银台登录失败（{desc}）：{str(e)}")
            raise

    def login_member(self, phone: str, desc: str):
        """会员登录（按实际页面逻辑补充）"""
        try:
            self.input_text({"id": "member-phone"}, phone, "输入会员手机号")
            self.click({"id": "member-login-btn"}, "点击会员登录按钮")
            logger.log("INFO", f"✅ 会员登录完成：{desc}（手机号：{phone}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 会员登录失败（{desc}）：{str(e)}")
            raise

    def input_pin(self, num: str, choose_num: str, status: int = 0, desc: str):
        """输入PIN码（按实际业务逻辑补充）"""
        try:
            # 此处按你的PIN码输入逻辑补充（如数字键盘点击）
            logger.log("INFO", f"✅ PIN码输入完成：{desc}（输入：{num}，选择：{choose_num}）")
        except Exception as e:
            logger.log("ERROR", f"❌ PIN码输入失败（{desc}）：{str(e)}")
            raise

    def run_yaml_case(self, yaml_path: str):
        """执行YAML用例（核心方法）"""
        try:
            # 读取YAML用例（自动替换${TEST_URL}）
            case_data = self.yaml_util.read_yaml(yaml_path)
            case_name = list(case_data.keys())[0]
            steps = case_data[case_name]
            logger.log("INFO", f"📢 开始执行用例：{case_name}")

            # 遍历执行用例步骤
            for step in steps:
                action = step.get("action")
                desc = step.get("desc", f"执行{action}操作")
                locator = step.get("locator")

                # 映射action到对应方法
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
                    self.input_pin(step["num"], step["choose_num"], step.get("status", 0), desc)
                elif action == "setup":
                    self.setup(step.get("url"))  # 调用setup方法（支持传URL）
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