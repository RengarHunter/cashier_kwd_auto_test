#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 11:07
@File: test_cashier_main.py
@Description: 
"""

import os
import pytest
import allure
from page_case.keyword_driver import KeywordDriver
from config.conf import cm

# 主流程YAML用例目录（可放多个YAML）
MAIN_YAML_DIR = os.path.join(cm.BASE_DIR, "page_elements/main")
# 获取所有主流程YAML文件
main_yaml_files = [f for f in os.listdir(MAIN_YAML_DIR) if f.endswith(".yaml")]


@allure.feature("收银台主流程测试（用餐高峰执行）")
@pytest.mark.main  # 主流程标记：高峰时段执行
class TestCashierMain:
    @pytest.mark.parametrize("yaml_file", main_yaml_files)
    @allure.story("执行主流程YAML用例")
    def test_main_case(self, keyword_driver: KeywordDriver, yaml_file):
        """参数化执行所有主流程YAML用例"""
        yaml_path = os.path.join(MAIN_YAML_DIR, yaml_file)
        allure.dynamic.title(f"主流程用例：{yaml_file[:-5]}")  # 去掉.yaml后缀
        keyword_driver.run_yaml_case(yaml_path)
