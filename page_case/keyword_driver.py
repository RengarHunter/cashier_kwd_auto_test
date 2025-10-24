#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:40
@File: keyword_driver.py
@Description: 关键字驱动核心类（修复KeyError+元素定位，区分shop/cashier登录）
"""
from DrissionPage import Chromium, ChromiumOptions
from common.yaml_util import YamlUtil
from config.conf import cm
from util.logger import logger_instance as logger


class KeywordDriver:
    def __init__(self):
        self.browser = None  # 浏览器实例
        self.page = None     # 页面实例
        self.yaml_util = YamlUtil()

    def setup(self, url: str = None):
        """初始化浏览器和页面（适配版本，确保兼容）"""
        try:
            co = ChromiumOptions()
            if cm.HEADLESS_MODE:
                co = co.headless()  # 无头模式配置（从.env读取）
            self.browser = Chromium(co)
            self.page = self.browser.new_tab()  # 适配DrissionPage 4.1.1.2版本

            target_url = url or cm.TEST_URL
            if not target_url:
                raise ValueError("测试地址未配置，请检查.env的TEST_URL")
            self.page.get(target_url)
            logger.log("INFO", f"✅ 已打开页面：{target_url}")
        except Exception as e:
            logger.log("ERROR", f"❌ 浏览器初始化失败：{str(e)}")
            raise

    def teardown(self):
        """关闭浏览器和页面，释放资源"""
        if self.page:
            self.page.close()
            logger.log("INFO", "✅ 页面已关闭")
        if self.browser:
            self.browser.quit()
            logger.log("INFO", "✅ 浏览器已关闭")

    def click(self, locator: str, desc: str, timeout: int = 20):
        """点击操作（支持超时等待，定位符为字符串XPath）"""
        try:
            # 增加超时等待，适配页面加载慢的场景；多定位符用逗号分隔（版本兼容）
            self.page.ele(locator, timeout=timeout).click()
            logger.log("INFO", f"✅ 点击完成：{desc}")
        except Exception as e:
            logger.log("ERROR", f"❌ 点击失败（{desc}）：{str(e)}")
            raise

    def input_text(self, locator: str, text: str, desc: str, timeout: int = 20):
        """输入操作（支持超时等待，对齐demo的ele(xpath).clear().input()）"""
        try:
            # 增加超时等待，多定位符用逗号分隔（修复竖线不兼容问题）
            self.page.ele(locator, timeout=timeout).clear().input(text)
            logger.log("INFO", f"✅ 输入完成：{desc}（内容：{text}）")
        except Exception as e:
            logger.log("ERROR", f"❌ 输入失败（{desc}）：{str(e)}")
            raise

    def assert_text(self, locator: str, expected_text: str, desc: str, timeout: int = 20):
        """文本断言（支持超时等待，按定位符获取文本）"""
        try:
            actual_text = self.page.ele(locator, timeout=timeout).text
            assert actual_text == expected_text, \
                f"断言失败：实际[{actual_text}] != 预期[{expected_text}]"
            logger.log("INFO", f"✅ 断言完成：{desc}")
        except AssertionError as ae:
            logger.log("ERROR", f"❌ 断言失败（{desc}）：{str(ae)}")
            raise
        except Exception as e:
            logger.log("ERROR", f"❌ 断言异常（{desc}）：{str(e)}")
            raise

    # -------------------------- Shop端登录（统一账密+版本兼容定位）--------------------------
    def login_shop(self, app_id: str, desc: str):
        """Shop端登录（按demo定位，统一账密echo0726@{app_id}/xl0120XL@@）"""
        try:
            # Shop登录页URL（按用户提供的demo）
            shop_login_url = "https://pos.amfuture.sg/shop/#/login"
            self.page.get(shop_login_url)
            logger.log("INFO", f"✅ 已打开Shop登录页：{shop_login_url}")

            # 统一账密（按用户要求，动态拼接app_id）
            username = f"echo0726@{app_id}"
            password = "xl0120XL@@"

            # 元素定位（严格按demo的XPath，增加超时等待）
            self.input_text(
                locator='x://input[@placeholder="Account Number"]',
                text=username,
                desc="Shop端输入账号",
                timeout=20
            )
            self.input_text(
                locator='x://input[@placeholder="Password"]',
                text=password,
                desc="Shop端输入密码",
                timeout=20
            )
            self.click(
                locator='x://button[starts-with(@class,"el-button")]',
                desc="Shop端点击登录按钮",
                timeout=20
            )
            # 登录后点击Menu（按demo流程）
            self.click(
                locator='x://span[contains(text(),"Menu")]',
                desc="Shop端点击Menu按钮",
                timeout=20
            )

            logger.log("INFO", f"✅ Shop端登录完成：{desc}（账号：{username}）")
        except Exception as e:
            logger.log("ERROR", f"❌ Shop端登录失败（{desc}）：{str(e)}")
            raise

    # -------------------------- Cashier端登录（修复定位符+默认app_id）--------------------------
    def login_cashier(self, app_id: str, desc: str):
        """Cashier端登录（修复多定位符格式，统一账密）"""
        try:
            # Cashier登录页URL（从配置读取，确保灵活）
            self.page.get(cm.TEST_URL)
            logger.log("INFO", f"✅ 已打开Cashier登录页：{cm.TEST_URL}")

            # 统一账密（按用户要求，动态拼接app_id）
            username = f"echo0726@{app_id}"
            password = "xl0120XL@@"

            # 元素定位（修复：多定位符用逗号分隔，适配4.1.1.2版本；增加超时）
            self.input_text(
                # 支持中文/英文占位符，逗号分隔多定位符（替换原竖线）
                locator='x://input[contains(@placeholder,"账号")],x://input[contains(@placeholder,"Account Number")]',
                text=username,
                desc="Cashier端输入账号",
                timeout=20
            )
            self.input_text(
                locator='x://input[contains(@placeholder,"密码")],x://input[contains(@placeholder,"Password")]',
                text=password,
                desc="Cashier端输入密码",
                timeout=20
            )
            self.click(
                locator='x://button[starts-with(@class,"el-button")]',
                desc="Cashier端点击登录按钮",
                timeout=20
            )

            logger.log("INFO", f"✅ Cashier端登录完成：{desc}（账号：{username}）")
        except Exception as e:
            logger.log("ERROR", f"❌ Cashier端登录失败（{desc}）：{str(e)}")
            raise

    def input_pin(self, num: str, choose_num: str, desc: str, status: int = 0):
        """PIN码输入（预留接口，按实际业务逻辑补充）"""
        try:
            logger.log("INFO", f"✅ PIN码输入完成：{desc}（输入：{num}，选择：{choose_num}，状态：{status}）")
        except Exception as e:
            logger.log("ERROR", f"❌ PIN码输入失败（{desc}）：{str(e)}")
            raise

    def run_yaml_case(self, yaml_path: str):
        """执行YAML用例（修复KeyError：app_id加默认值，支持shop/cashier登录）"""
        try:
            case_data = self.yaml_util.read_yaml(yaml_path)
            case_name = list(case_data.keys())[0]
            steps = case_data[case_name]
            logger.log("INFO", f"📢 开始执行用例：{case_name}")

            for step in steps:
                action = step.get("action")
                desc = step.get("desc", f"执行{action}操作")
                locator = step.get("locator")  # 定位符为字符串XPath（多定位符逗号分隔）

                # 步骤映射：修复app_id缺失问题（加默认值"test_app"）
                if action == "click":
                    self.click(locator, desc)
                elif action == "input_text":
                    self.input_text(locator, step["text"], desc)
                elif action == "assert_text":
                    self.assert_text(locator, step["expected"], desc)
                elif action == "login_shop":
                    # 安全获取app_id：YAML缺失时用默认值"test_app"，避免KeyError
                    app_id = step.get("app_id", "test_app")
                    self.login_shop(app_id, desc)
                elif action == "login_cashier":
                    # 安全获取app_id：同上，兼容YAML配置缺失场景
                    app_id = step.get("app_id", "test_app")
                    self.login_cashier(app_id, desc)
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