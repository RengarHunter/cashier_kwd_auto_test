#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 11:07
@File: test_cashier_other.py
@Description: 
"""

import os
import pytest
import allure
from page_case.keyword_driver import KeywordDriver
from config.conf import cm

# 非主流程YAML用例目录
OTHER_YAML_DIR = os.path.join(cm.BASE_DIR, "page_elements/other")
other_yaml_files = [f for f in os.listdir(OTHER_YAML_DIR) if f.endswith(".yaml")]


@allure.feature("收银台非主流程测试（闲时执行）")
@pytest.mark.other  # 非主流程标记：闲时执行
class TestCashierOther:
    @pytest.mark.parametrize("yaml_file", other_yaml_files)
    @allure.story("执行非主流程YAML用例")
    def test_other_case(self, keyword_driver: KeywordDriver, yaml_file):
        """参数化执行所有非主流程YAML用例"""
        yaml_path = os.path.join(OTHER_YAML_DIR, yaml_file)
        allure.dynamic.title(f"非主流程用例：{yaml_file[:-5]}")
        keyword_driver.run_yaml_case(yaml_path)
