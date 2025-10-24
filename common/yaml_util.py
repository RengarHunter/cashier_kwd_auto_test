#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 10:39
@File: yaml_util.py
@Description: 
"""

import yaml
import os
from util.logger import logger


class YamlUtil:
    def __init__(self):
        pass

    def read_yaml(self, yaml_path):
        """读取YAML文件内容"""
        try:
            if not os.path.exists(yaml_path):
                raise FileNotFoundError(f"YAML文件不存在: {yaml_path}")

            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            logger.log("Info", f"成功读取YAML文件: {yaml_path}")
            return data
        except Exception as e:
            logger.log("ERROR", f"读取YAML文件失败: {str(e)}")
            raise e

    def write_yaml(self, yaml_path, data):
        """写入数据到YAML文件"""
        try:
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            logger.log("Info", f"成功写入YAML文件: {yaml_path}")
        except Exception as e:
            logger.log("ERROR", f"写入YAML文件失败: {str(e)}")
            raise e
