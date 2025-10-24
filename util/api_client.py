#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/09/03
@File: api_client.py
@Description: 通用 API 客户端，支持 Session Cookie 登录、Token 登录，并可自动判断登录方式
"""

import requests


class APIClient:
    def __init__(self, base_url: str, debug: bool = True):
        """
        初始化
        :param base_url: API 基础地址，例如 "https://pos.amfuture.sg/index.php"
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.token = None
        self.debug = debug

    def login_with_session(self, login_path: str, username: str, password: str,
                           user_field="user_name", pass_field="password"):
        """
        用 Session Cookie 登录
        """
        login_url = f"{self.base_url}{login_path}"
        payload = {user_field: username, pass_field: password}
        resp = self.session.post(login_url, data=payload)

        if self.debug:
            print(f"[DEBUG] Session 登录请求 {login_url} payload={payload}")
            print(f"[DEBUG] 响应: {resp.status_code} {resp.text[:200]}")

        return resp

    def login_with_token(self, login_path: str, username: str, password: str,
                         user_field="user_name", pass_field="password", token_field="token"):
        """
        用 Token 登录
        """
        login_url = f"{self.base_url}{login_path}"
        payload = {user_field: username, pass_field: password}
        resp = self.session.post(login_url, json=payload)
        data = {}

        try:
            data = resp.json()
        except Exception:
            pass

        self.token = data.get(token_field)
        if self.token:
            # 自动带上 Authorization
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            if self.debug:
                print(f"[INFO] Token 登录成功, token={self.token[:10]}...")

        return self.token

    def auto_login(self, login_path: str, username: str, password: str,
                   user_field="user_name", pass_field="password", token_field="token"):
        """
        自动判断登录方式：
        - 先尝试 Session 登录
        - 如果响应中包含 token，则自动切换为 Token 模式
        """
        resp = self.login_with_session(
            login_path, username, password,
            user_field=user_field, pass_field=pass_field
        )

        try:
            data = resp.json()
            if token_field in data:
                self.token = data[token_field]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                if self.debug:
                    print(f"[INFO] 自动识别到 Token 登录模式, token={self.token[:10]}...")
        except Exception:
            if self.debug:
                print("[INFO] 使用 Session Cookie 登录模式")

        return resp

    def get(self, path: str, headers=None, params=None):
        """发送 GET 请求（自动带 Cookie 或 Token）"""
        url = f"{self.base_url}{path}"
        merged_headers = headers.copy() if headers else {}
        return self.session.get(url, headers=merged_headers, params=params)

    def post(self, path: str, headers=None, data=None, json=None):
        """发送 POST 请求（自动带 Cookie 或 Token）"""
        url = f"{self.base_url}{path}"
        merged_headers = headers.copy() if headers else {}
        return self.session.post(url, headers=merged_headers, data=data, json=json)
