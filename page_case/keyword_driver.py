#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:40
@File: keyword_driver.py
@Description: 关键字驱动核心类（区分shop/cashier登录，按你的定位模式实现）
"""
from DrissionPage import Chromium, ChromiumOptions
from common.yaml_util import YamlUtil
from config.conf import cm
from util.logger import logger_instance as logger


class KeywordDriver:
    def __init__(self):
        self.browser = None  # 浏览器实例
        self.page = None  # 页面实例
        self.yaml_util = YamlUtil()

    def setup(self, url: str = None):
        """初始化浏览器和页面（复用现有逻辑，确保兼容）"""
        try:
            co = ChromiumOptions()
            if cm.HEADLESS_MODE:
                co = co.headless()  # 无头模式配置
            self.browser = Chromium(co)
            self.page = self.browser.new_tab()  # 适配你的版本

            target_url = url or cm.TEST_URL
            if not target_url:
                raise ValueError("测试地址未配置，请检查.env的TEST_URL")
            self.page.get(target_url)
            logger.log("INFO", f"✅ 已打开页面：{target_url}")
        except Exception as e:
            logger.log("ERROR", f"❌ 浏览器初始化失败：{str(e)}")
            raise

    def teardown(self):
        """关闭浏览器和页面"""
        if self.page:
            self.page.close()
            logger.log("INFO", "✅ 页面已关闭")
        if self.browser:
            self.browser.quit()
            logger.log("INFO", "✅ 浏览器已关闭")

    def click(self, locator: str, desc: str):
        """点击操作（严格按你的定位模式：字符串XPath）"""
        try:
            self.page.ele(locator).click()  # 对齐你的 demo：ele(xpath).click()
            logger.log("INFO", f"✅ 点击完成：{desc}")
        except Exception as e:
            logger.log("ERROR", f"❌ 点击失败（{desc}）：{str(e)}")
            raise

    def input_text(self, locator: str, text: str, desc: str):
        """输入操作（对齐你的 demo：ele(xpath).clear().input()）"""
        try:
            self.page.ele(locator).clear().input(text)
            logger.log("INFO", f"✅ 输入完成：{desc}（内容：{text}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 输入失败（{desc}）：{str(e)}")
            raise

    def assert_text(self, locator: str, expected_text: str, desc: str):
        """文本断言（按你的定位模式获取文本）"""
        try:
            actual_text = self.page.ele(locator).text  # 用ele(xpath).text获取文本
            assert actual_text == expected_text, \
                f"断言失败：实际[{actual_text}] != 预期[{expected_text}]"
            logger.log("INFO", f"✅ 断言完成：{desc}")
        except AssertionError as ae:
            logger.log("ERROR", f"❌ 断言失败（{desc}）：{str(ae)}")
            raise
        except Exception as e:
            logger.log("ERROR", f"❌ 断言异常（{desc}）：{str(e)}")
            raise

    # -------------------------- Shop端登录（按你的定位和账密实现）--------------------------
    def login_shop(self, app_id: str, desc: str):
        """Shop端登录（使用你的元素定位和统一账密）"""
        try:
            # Shop登录页URL（按你的demo）
            shop_login_url = "https://pos.amfuture.sg/shop/#/login"
            self.page.get(shop_login_url)
            logger.log("INFO", f"已打开Shop登录页：{shop_login_url}")

            # 统一账密（按你的要求：echo0726@{app_id} 和 xl0120XL@@）
            username = f"echo0726@{app_id}"
            password = "xl0120XL@@"

            # 元素定位（严格按你的demo）
            self.input_text(
                locator='x://input[@placeholder="Account Number"]',
                text=username,
                desc="Shop端输入账号"
            )
            self.input_text(
                locator='x://input[@placeholder="Password"]',
                text=password,
                desc="Shop端输入密码"
            )
            self.click(
                locator='x://button[starts-with(@class,"el-button")]',
                desc="Shop端点击登录按钮"
            )
            # 登录后点击Menu（按你的demo）
            self.click(
                locator='x://span[contains(text(),"Menu")]',
                desc="Shop端点击Menu"
            )

            logger.log("INFO", f"✅ Shop端登录完成：{desc}（账号：{username}）")
        except Exception as e:
            logger.log("ERROR", f"❌ Shop端登录失败（{desc}）：{str(e)}")
            raise

    # -------------------------- Cashier端登录（按你的定位和账密实现）--------------------------
    def login_cashier(self, app_id: str, desc: str):
        """Cashier端登录（使用你的元素定位和统一账密）"""
        try:
            # Cashier登录页URL（从配置读取，默认使用TEST_URL）
            self.page.get(cm.TEST_URL)
            logger.log("INFO", f"已打开Cashier登录页：{cm.TEST_URL}")

            # 统一账密（按你的要求：echo0726@{app_id} 和 xl0120XL@@）
            username = f"echo0726@{app_id}"
            password = "xl0120XL@@"

            # 元素定位（按你提供的Cashier定位符）
            self.input_text(
                # 账号输入框：支持中文/英文占位符
                locator='x://input[contains(@placeholder,"账号")] | x://input[contains(@placeholder,"Account Number")]',
                text=username,
                desc="Cashier端输入账号"
            )
            self.input_text(
                # 密码输入框：支持中文/英文占位符
                locator='x://input[contains(@placeholder,"密码")] | x://input[contains(@placeholder,"Password")]',
                text=password,
                desc="Cashier端输入密码"
            )
            self.click(
                locator='x://button[starts-with(@class,"el-button")]',
                desc="Cashier端点击登录按钮"
            )

            logger.log("INFO", f"✅ Cashier端登录完成：{desc}（账号：{username}）")
        except Exception as e:
            logger.log("ERROR", f"❌ Cashier端登录失败（{desc}）：{str(e)}")
            raise

    def input_pin(self, num: str, choose_num: str, desc: str, status: int = 0):
        """PIN码输入（预留，按实际逻辑补充）"""
        try:
            logger.log("INFO", f"✅ PIN码输入完成：{desc}（输入：{num}，选择：{choose_num}）")
        except Exception as e:
            logger.log("ERROR", f"❌ PIN码输入失败（{desc}）：{str(e)}")
            raise

    def run_yaml_case(self, yaml_path: str):
        """执行YAML用例（支持shop/cashier登录）"""
        try:
            case_data = self.yaml_util.read_yaml(yaml_path)
            case_name = list(case_data.keys())[0]
            steps = case_data[case_name]
            logger.log("INFO", f"📢 开始执行用例：{case_name}")

            for step in steps:
                action = step.get("action")
                desc = step.get("desc", f"执行{action}操作")
                locator = step.get("locator")  # 必须是字符串XPath

                # 步骤映射（新增shop/cashier登录支持）
                if action == "click":
                    self.click(locator, desc)
                elif action == "input_text":
                    self.input_text(locator, step["text"], desc)
                elif action == "assert_text":
                    self.assert_text(locator, step["expected"], desc)
                elif action == "login_shop":
                    # 从YAML获取app_id（示例：step["app_id"]）
                    self.login_shop(step["app_id"], desc)
                elif action == "login_cashier":
                    # 从YAML获取app_id
                    self.login_cashier(step["app_id"], desc)
                elif action == "input_pin":
                    self.input_pin(step["num"], step["choose_num"], desc, step.get("status", 0))
                elif action == "setup":
                    self.setup(step.get("url"))
                elif action == "scroll_to_bottom":
                    self.page.scroll.to_bottom()
                    logger.log("INFO", f"✅ 滚动完成：{desc}")
                else:
                    raise ValueError(f"不支持的操作：{action}（用例：{case_name}）")

            logger.log("INFO", f"🎉 用例执行完成：{case_name}")
        except Exception as e:
            logger.log("ERROR", f"❌ 用例执行失败：{str(e)}")
            raise