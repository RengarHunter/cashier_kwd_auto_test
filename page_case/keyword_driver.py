#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:39
@File: keyword_driver.py
@Description: 
"""

from DrissionPage import WebPage, ChromiumOptions
from common.yaml_util import YamlUtil
from common.utils import click_pin, remove_modal_overlay
from util.logger import Logger
from util.times import sleep
from config.conf import cm
import allure
import os

logger = Logger()


class KeywordDriver:
    def __init__(self):
        self.page: WebPage = None
        self.yaml_util = YamlUtil()

    def setup(self, url: str = None):
        """初始化DrissionPage浏览器"""
        co = ChromiumOptions()
        if cm.HEADLESS_MODE:
            co.headless(True)
        co.set_browser_path(cm.CHROME_PATH)  # 若需指定Chrome路径，在.env添加
        self.page = WebPage(co)
        if url:
            self.page.get(url)
            sleep(3)
        logger.info(f"浏览器初始化完成，访问URL: {url}")
        return self.page

    def teardown(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()
        logger.info("浏览器已关闭")

    # ---------------------- 通用关键字 ----------------------
    @allure.step("{desc}")
    def click(self, locator: list, desc: str = "点击元素"):
        try:
            elem = self._get_element(locator)
            elem.click()
            sleep(1)
            logger.info(f"点击元素: {desc}")
        except Exception as e:
            self._handle_exception(desc, e)

    @allure.step("{desc}")
    def input_text(self, locator: list, text: str, desc: str = "输入文本"):
        try:
            elem = self._get_element(locator)
            elem.clear()
            elem.input(text)
            logger.info(f"输入文本: {text} ({desc})")
        except Exception as e:
            self._handle_exception(desc, e)

    @allure.step("{desc}")
    def assert_text(self, locator: list, expected: str, desc: str = "验证文本"):
        try:
            actual = self._get_element(locator).text.strip()
            assert actual == expected, f"预期[{expected}] != 实际[{actual}]"
            logger.info(f"文本验证成功: {desc}")
        except AssertionError as e:
            self._handle_exception(desc, e)
        except Exception as e:
            self._handle_exception(desc, e)

    # ---------------------- 业务关键字（收银台专属） ----------------------
    @allure.step("收银台登录：用户名={username}")
    def login_cashier(self, username: str, password: str, pin: str, desc: str = "收银台登录"):
        """收银台完整登录流程（含PIN输入）"""
        try:
            # 输入账号密码
            self.input_text(["xpath", '//input[@placeholder="用户名"]'], username, "输入用户名")
            self.input_text(["xpath", '//input[@placeholder="密码"]'], password, "输入密码")
            self.click(["xpath", '//button[contains(text(), "登录")]'], "点击登录按钮")
            sleep(5)

            # 输入PIN码
            click_pin(self.page, pin, choose_num=1)
            self.click(["xpath", '//button[contains(text(), "确认")]'], "确认PIN码")
            sleep(3)
            logger.info("收银台登录成功")
        except Exception as e:
            self._handle_exception(desc, e)

    @allure.step("会员登录：手机号={phone}")
    def login_member(self, phone: str, desc: str = "会员登录"):
        """会员登录流程"""
        try:
            self.click(["xpath", '//button[contains(text(), "会员支付")]'], "点击会员支付")
            self.input_text(["xpath", '//input[@placeholder="手机号"]'], phone, "输入会员手机号")
            self.click(["xpath", '//button[contains(text(), "确认")]'], "确认会员登录")
            sleep(2)
            logger.info(f"会员登录成功：{phone}")
        except Exception as e:
            self._handle_exception(desc, e)

    @allure.step("输入PIN码：{num}")
    def input_pin(self, num: str, choose_num: int, status=0, desc: str = "输入PIN码"):
        """单独调用PIN输入（如充值、支付时）"""
        try:
            click_pin(self.page, num, choose_num, status)
        except Exception as e:
            self._handle_exception(desc, e)

    # ---------------------- 内部工具方法 ----------------------
    def _get_element(self, locator: list, timeout: int = cm.TEST_TIMEOUT):
        """获取元素（支持xpath/id/css/text）"""
        loc_type, loc_val = locator
        try:
            if loc_type == "xpath":
                return self.page.ele(xpath=loc_val, timeout=timeout)
            elif loc_type == "id":
                return self.page.ele(id=loc_val, timeout=timeout)
            elif loc_type == "css":
                return self.page.ele(css=loc_val, timeout=timeout)
            elif loc_type == "text":
                return self.page.ele(text=loc_val, timeout=timeout)
            else:
                raise ValueError(f"不支持的定位方式: {loc_type}")
        except Exception as e:
            raise Exception(f"元素获取失败 [{loc_type}:{loc_val}]: {str(e)}")

    def _handle_exception(self, desc: str, e: Exception):
        """异常处理：日志+截图+Allure附件"""
        error_msg = f"{desc}失败: {str(e)}"
        logger.error(error_msg)
        # 截图
        screenshot_path = self._take_screenshot()
        allure.attach.file(screenshot_path, name=f"错误截图_{desc}", attachment_type=allure.attachment_type.PNG)
        raise e  # 抛出异常，让用例失败

    def _take_screenshot(self):
        """生成截图（按时间命名）"""
        timestamp = time.strftime("%Y%m%d%H%M%S")
        os.makedirs(cm.SCREENSHOT_DIR, exist_ok=True)
        path = f"{cm.SCREENSHOT_DIR}/error_{timestamp}.png"
        self.page.save_screenshot(path)
        return path

    def run_yaml_case(self, yaml_path: str):
        """执行单个YAML用例"""
        try:
            # 读取YAML用例
            case_data = self.yaml_util.read_yaml(yaml_path)
            case_name = list(case_data.keys())[0]
            steps = case_data[case_name]
            logger.info(f"开始执行用例：{case_name}")

            # 执行步骤
            for step in steps:
                action = step.get("action")
                desc = step.get("desc", f"执行{action}")
                locator = step.get("locator")

                # 映射action到关键字方法
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
                elif action == "scroll_to_bottom":
                    self.page.scroll.to_bottom()
                    logger.info(desc)
                else:
                    raise ValueError(f"不支持的操作: {action}")

            logger.info(f"用例执行完成：{case_name}")
        except Exception as e:
            logger.error(f"用例执行失败：{str(e)}")
            raise
