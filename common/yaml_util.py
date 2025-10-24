#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:40
@File: yaml_util.py
@Description: YAML文件读取工具（支持变量替换）
"""
import yaml
import os
from config.conf import cm
from util.logger import logger_instance as logger


class YamlUtil:
    def read_yaml(self, yaml_path: str):
        """
        读取YAML用例文件，并自动替换变量（如${TEST_URL}）
        :param yaml_path: YAML文件路径
        :return: 解析后的YAML字典数据
        """
        try:
            # 1. 检查YAML文件是否存在
            if not os.path.exists(yaml_path):
                raise FileNotFoundError(f"YAML用例文件不存在：{yaml_path}")

            # 2. 读取YAML内容并替换变量
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()
                # 替换${TEST_URL}为cm.TEST_URL（从.env读取的配置）
                yaml_content = yaml_content.replace("${TEST_URL}", cm.TEST_URL)
                # 如需替换其他变量（如${CASHIER_USER}），可在此处添加
                yaml_content = yaml_content.replace("${CASHIER_USER}", cm.CASHIER_USER)
                yaml_content = yaml_content.replace("${CASHIER_PIN}", cm.CASHIER_PIN)

            # 3. 解析YAML内容（安全加载，避免执行恶意代码）
            case_data = yaml.safe_load(yaml_content)
            if not case_data:
                raise ValueError(f"YAML用例文件为空：{yaml_path}")

            logger.log("INFO", f"✅ 成功读取YAML用例：{os.path.basename(yaml_path)}")
            return case_data

        except yaml.YAMLError as ye:
            logger.log("ERROR", f"❌ YAML格式解析错误（{yaml_path}）：{str(ye)}")
            raise
        except Exception as e:
            logger.log("ERROR", f"❌ 读取YAML用例失败（{yaml_path}）：{str(e)}")
            raise

    def write_yaml(self, data: dict, yaml_path: str):
        """
        写入数据到YAML文件（可选功能，保留备用）
        :param data: 要写入的字典数据
        :param yaml_path: 目标YAML文件路径
        """
        try:
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, encoding="utf-8", allow_unicode=True, sort_keys=False)
            logger.log("INFO", f"✅ 成功写入YAML文件：{yaml_path}")
        except Exception as e:
            logger.log("ERROR", f"❌ 写入YAML文件失败（{yaml_path}）：{str(e)}")
            raise