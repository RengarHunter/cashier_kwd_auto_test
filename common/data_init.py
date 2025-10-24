#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 11:09
@File: data_init.py
@Description: 收银台测试数据初始化（清空订单/优惠券、发送测试券、登录态管理）
"""

import json
import time
import requests
from config.conf import cm  # 项目全局配置
from util.logger import logger_instance  # 项目日志工具

# 日志实例（适配自定义Logger类，仅支持log(level, msg)方法）
logger = logger_instance

# 测试常量（集中管理，避免硬编码；后续可迁移到cm配置中）
TEST_CONSTANTS = {
    "APP_ID": "10046",
    "MEMBER_USER_ID": "136680",  # 测试会员ID
    "TEST_COUPON_ID": "14879",   # 测试优惠券ID
    "CASHIER_LOGIN_URL": "https://pos.amfuture.sg/index.php/cashier/passport/login",
    "CASHIER_COUPON_URL": "https://pos.amfuture.sg/index.php/shop/plus.coupon.coupon/index",
    "DEL_MEMBER_ORDER_URL": "https://pos.amfuture.sg/api/autotest/delUserOrder",
    "DEL_ALL_COUPON_URL": "https://pos.amfuture.sg/api/autotest/delUserCoupon",
    "SEND_COUPON_URL": "https://pos.amfuture.sg/index.php/shop/plus.coupon.receive/SendCoupon",
    "GET_STAY_ORDER_URL": "https://pos.amfuture.sg/index.php/cashier/order.CartHandle/getStayList",
    "DEL_STAY_ORDER_URL": "https://pos.amfuture.sg/index.php/cashier/order.CartHandle/setDelCart"
}


class CashierDataInit:
    """收银台测试数据初始化工具类"""
    def __init__(self):
        # 复用会话（保持登录态，减少重复请求）
        self.session = requests.Session()
        # 存储登录后的headers（供后续接口使用）
        self.shop_headers = None  # 商家后台headers
        self.cashier_headers = None  # 收银台后台headers
        # 请求超时时间（防止网络阻塞）
        self.request_timeout = 15

    def login_shop(self):
        """
        登录商家后台，获取并存储headers
        :return: 商家后台headers（dict）
        :raise: Exception - 登录失败时抛出异常
        """
        if self.shop_headers:
            logger.log("INFO", "商家后台已登录，无需重复登录")
            return self.shop_headers

        try:
            login_data = {
                "username": cm.SHOP_USER,
                "password": cm.SHOP_PWD
            }
            # 发送登录请求（带超时）
            resp = self.session.post(
                url=cm.SHOP_LOGIN_URL,
                data=login_data,
                timeout=self.request_timeout
            )
            resp.raise_for_status()  # 触发HTTP错误（如404/500）
            resp_json = resp.json()

            # ---------------- 关键修正1：修正成功响应码（0→1） ----------------
            # 从接口文档可知：code=1代表成功（如delUserOrder、delUserCoupon）
            code = resp_json.get("code")
            if code is None:
                raise Exception("登录响应缺失'code'字段")
            if code != 1:  # 原来写的是 !=0，现在修正为 !=1
                raise Exception(f"登录响应异常: code={code}, msg={resp_json.get('msg', '未知错误')}")

            # ---------------- 关键修正2：校验data和token是否存在 ----------------
            data = resp_json.get("data")
            if not data:
                raise Exception("登录响应缺失'data'字段")
            token = data.get("token")
            if not token:
                raise Exception("登录响应的'data'中缺失'token'字段")

            # 构建并存储headers
            self.shop_headers = {
                "accept": "application/json, text/plain, /",
                "access-token": token,  # 使用校验后的token
                "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                "cookie": "; ".join([f"{k}={v}" for k, v in self.session.cookies.items()])
            }
            logger.log("INFO", "✅ 商家后台登录成功")
            return self.shop_headers

        except requests.exceptions.RequestException as e:
            raise Exception(f"商家后台登录网络错误: {str(e)}") from e
        except Exception as e:
            raise Exception(f"商家后台登录失败: {str(e)}") from e

    def login_cashier_backend(self):
        """登录收银台后台，获取并存储headers"""
        if self.cashier_headers:
            logger.log("INFO", "收银台后台已登录，无需重复登录")
            return self.cashier_headers

        try:
            # 1. 发送收银台登录请求
            login_data = {
                "user_name": cm.CASHIER_USER,
                "password": cm.CASHIER_PWD,
                "op_pin_code": cm.CASHIER_PIN
            }
            resp = self.session.post(
                url=TEST_CONSTANTS["CASHIER_LOGIN_URL"],
                data=login_data,
                timeout=self.request_timeout
            )
            resp.raise_for_status()
            login_resp = resp.json()

            # ---------------- 同步修正：成功响应码（0→1，根据实际接口调整） ----------------
            code = login_resp.get("code")
            if code is None:
                raise Exception("收银台登录响应缺失'code'字段")
            if code != 1:  # 原来写的是 !=0，根据实际接口响应修正
                raise Exception(f"收银台登录响应异常: code={code}, msg={login_resp.get('msg', '未知错误')}")

            # 2. 访问优惠券页面获取完整headers
            coupon_resp = self.session.post(
                url=TEST_CONSTANTS["CASHIER_COUPON_URL"],
                timeout=self.request_timeout
            )
            coupon_resp.raise_for_status()

            self.cashier_headers = dict(coupon_resp.request.headers)
            logger.log("INFO", "✅ 收银台后台登录成功")
            return self.cashier_headers

        except requests.exceptions.RequestException as e:
            raise Exception(f"收银台后台登录网络错误: {str(e)}") from e
        except Exception as e:
            raise Exception(f"收银台后台登录失败: {str(e)}") from e

    def _clear_member_orders(self):
        """子方法：清空测试会员的所有订单（拆分冗余逻辑，提升可读性）"""
        try:
            # 构造请求参数（避免URL硬编码）
            params = {
                "app_id": TEST_CONSTANTS["APP_ID"],
                "user_id": TEST_CONSTANTS["MEMBER_USER_ID"]
            }
            resp = self.session.get(
                url=TEST_CONSTANTS["DEL_MEMBER_ORDER_URL"],
                headers=self.shop_headers,
                params=params,
                timeout=self.request_timeout
            )
            resp.raise_for_status()
            logger.log("INFO", f"✅ 清空会员订单成功，响应: {resp.text[:100]}")  # 截断长响应
        except Exception as e:
            raise Exception(f"清空会员订单失败: {str(e)}") from e

    def _clear_all_coupons(self):
        """子方法：清空所有测试优惠券"""
        try:
            params = {"app_id": TEST_CONSTANTS["APP_ID"]}
            resp = self.session.get(
                url=TEST_CONSTANTS["DEL_ALL_COUPON_URL"],
                headers=self.shop_headers,
                params=params,
                timeout=self.request_timeout
            )
            resp.raise_for_status()
            logger.log("INFO", f"✅ 清空所有优惠券成功，响应: {resp.text[:100]}")
        except Exception as e:
            raise Exception(f"清空优惠券失败: {str(e)}") from e

    def _send_test_coupon(self):
        """子方法：给测试会员发送$10优惠券"""
        try:
            send_data = {
                "send_type": "3",
                "coupon_id": "0",
                "user_level": "",
                "user_ids": TEST_CONSTANTS["MEMBER_USER_ID"],
                "name": "$10",
                "expend_money[0]": "0",
                "expend_money[1]": "0",
                "coupon_ids[0]": TEST_CONSTANTS["TEST_COUPON_ID"]
            }
            resp = self.session.post(
                url=TEST_CONSTANTS["SEND_COUPON_URL"],
                headers=self.shop_headers,
                data=send_data,
                timeout=self.request_timeout
            )
            resp.raise_for_status()
            logger.log("INFO", f"✅ 发送$10优惠券成功，响应: {resp.text[:100]}")
        except Exception as e:
            raise Exception(f"发送优惠券失败: {str(e)}") from e

    def _clear_stay_orders(self):
        """子方法：清空收银台挂单数据"""
        try:
            # 1. 获取挂单列表
            resp = self.session.post(
                url=TEST_CONSTANTS["GET_STAY_ORDER_URL"],
                headers=self.cashier_headers,
                timeout=self.request_timeout
            )
            resp.raise_for_status()
            stay_data = resp.json()

            # 2. 有挂单则删除
            product_list = stay_data.get("data", {}).get("productList", [])
            if not product_list:
                logger.log("INFO", "ℹ️ 无挂单数据，无需清理")
                return

            # 处理第一个挂单（原逻辑保留，可扩展批量处理）
            cart_no = product_list[0].get("cart_no")
            if not cart_no:
                logger.log("WARNING", "挂单数据中未找到cart_no")
                return

            # 3. 删除挂单
            del_resp = self.session.post(
                url=TEST_CONSTANTS["DEL_STAY_ORDER_URL"],
                headers=self.cashier_headers,
                json={"cart_no": cart_no},  # 注意用json格式（原逻辑正确）
                timeout=self.request_timeout
            )
            del_resp.raise_for_status()
            logger.log("INFO", f"✅ 清空挂单成功，cart_no: {cart_no}")

        except Exception as e:
            raise Exception(f"清空挂单失败: {str(e)}") from e

    def clear_test_data(self):
        """
        主方法：完整测试数据清理流程
        流程：登录双后台 → 清空会员订单 → 清空优惠券 → 发送测试券 → 清空挂单
        :raise: Exception - 任一环节失败则抛出异常
        """
        logger.log("INFO", "=" * 60)
        logger.log("INFO", "📢 开始执行测试数据初始化流程")
        logger.log("INFO", "=" * 60)

        try:
            # 1. 前置：登录双后台（确保后续接口有权限）
            self.login_shop()
            self.login_cashier_backend()

            # 2. 执行数据清理子步骤（顺序不可乱）
            self._clear_member_orders()
            self._clear_all_coupons()
            self._send_test_coupon()
            self._clear_stay_orders()

            # 3. 后置：等待数据同步（原逻辑保留，可根据实际调整）
            time.sleep(2)
            logger.log("INFO", "=" * 60)
            logger.log("INFO", "🎉 测试数据初始化流程执行完成")
            logger.log("INFO", "=" * 60)

        except Exception as e:
            # 统一捕获所有异常，输出完整错误信息
            error_msg = f"测试数据初始化失败: {str(e)}"
            logger.log("ERROR", error_msg)
            logger.log("INFO", "=" * 60)
            raise Exception(error_msg) from e  # 抛出异常，终止测试用例


# 测试代码（单独运行时验证功能，集成到测试框架时不会执行）
if __name__ == "__main__":
    try:
        data_init = CashierDataInit()
        data_init.clear_test_data()
    except Exception as e:
        logger.log("ERROR", f"独立测试失败: {str(e)}")