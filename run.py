#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: XieLong
@Date: 2025/10/24 11:07
@File: run.py
@Description: 
"""

import os
import subprocess
import sys
import json
from util.feishu_dev import fsdev
from util.feishu_myself import fsm
from util.feishu_talk import fst
from config.conf import cm
from util.logger import logger_instance  # 导入你的日志单例

# 日志别名（简化调用）
logger = logger_instance
WIN = sys.platform.startswith('win')

# 定义Allure相关路径（基于你的cm.BASE_DIR）
ALLURE_RESULTS_DIR = os.path.join(cm.BASE_DIR, "allure-results")
ALLURE_REPORT_DIR = os.path.join(cm.BASE_DIR, "allure-report")

def delete_report_file():
    """删除历史报告文件（适配你的cm.json_dir()）"""
    try:
        # 你的JSON目录通过cm.json_dir()获取（注意是方法，需要调用）
        report_path = os.path.join(cm.json_dir(), "report.txt")
        if os.path.exists(report_path):
            os.remove(report_path)
            logger.log("INFO", f"已删除历史报告文件: {report_path}")
        else:
            logger.log("INFO", "无历史报告文件需要删除")
    except Exception as e:
        logger.log("ERROR", f"删除报告文件时发生错误: {e}")

def execute_test_steps(test_file=None, case_mark=None):
    """执行测试步骤（使用cm和正确的Allure路径）"""
    # 发送通知
    if test_file:
        fsm.sendTextmessage(f'开始运行脚本:\t{test_file}')
    elif case_mark:
        case_type = "主流程" if case_mark == "main" else "非主流程"  # 直接用标记字符串（你的cm中未定义，可在cm中补充）
        fsm.sendTextmessage(f'开始运行{case_type}用例（标记：{case_mark}）')

    # 构建Pytest命令（使用上面定义的Allure路径）
    pytest_cmd = f"pytest --alluredir {ALLURE_RESULTS_DIR} --clean-alluredir"
    if case_mark:
        pytest_cmd += f" -m {case_mark}"
    if test_file:
        pytest_cmd += f" {test_file}"

    # 生成Allure报告
    allure_cmd = f"allure generate {ALLURE_RESULTS_DIR} -c -o {ALLURE_REPORT_DIR}"
    steps = [pytest_cmd, allure_cmd]

    # 执行命令
    for step in steps:
        command = f"call {step}" if WIN else step
        try:
            subprocess.run(command, shell=True, check=True)
            logger.log("INFO", f"执行命令成功: {step}")
        except subprocess.CalledProcessError as e:
            logger.log("ERROR", f"执行命令失败: {step}, 错误: {e}")
            raise

def terminate_java_process():
    try:
        if WIN:
            os.popen('taskkill /F /im java.exe')
        else:
            subprocess.run(['pkill', '-9', '-f', 'java'], check=True)
        logger.log("INFO", "Java进程已终止")
    except Exception as e:
        logger.log("ERROR", f"终止Java进程时发生错误: {e}")

def read_test_report():
    try:
        # 读取报告JSON（使用cm.json_dir()）
        report_path = os.path.join(cm.json_dir(), "report.json")
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.log("WARNING", f"测试报告文件未找到: {report_path}")
        return None
    except json.JSONDecodeError as e:
        logger.log("ERROR", f"JSON文件解析错误: {e}")
        return None

def classify_test_results(results):
    # 保持原有逻辑
    temp_list1 = [(res["name"], res["outcome"], res.get("call", {}).get("stdout", "")) for res in
                  results['report']["tests"]]
    temp_list2 = [(i[0].split('::')[1], i[1], i[2]) for i in temp_list1 if i[1] != 'skipped']

    pass_status = {}
    failed_details = {}
    for testcase, status, error_message in temp_list2:
        if status != "passed":
            failed_details[testcase] = error_message
        pass_status.setdefault(testcase, set()).add(status)

    passed_tests = [k for k, v in pass_status.items() if 'passed' in v]
    failed_tests = [k for k, v in pass_status.items() if 'passed' not in v]
    return passed_tests, failed_tests, failed_details

def send_test_report(passed_tests, failed_tests, temp_dict, temp_dict_en, failed_details, status=1):
    # 保持原有逻辑
    def format_message(tests, is_passed, use_en=False):
        if not tests:
            return ""
        symbol = '✅' if is_passed else '❌'
        messages = []
        for test in tests:
            desc = temp_dict_en.get(test, test) if use_en else temp_dict.get(test, test)
            msg = f"{symbol} {desc}"
            if not is_passed and test in failed_details:
                msg += f"\n报错: {str(failed_details[test])[:200]}"
            messages.append(msg + "\n" + "-"*50)
        return "\n".join(messages)

    pass_msgs = format_message(passed_tests, is_passed=True)
    error_msgs = format_message(failed_tests, is_passed=False)
    final_msg = f"{pass_msgs}\n{error_msgs}\n测试文档链接:https://nt2mf25usb.feishu.cn/wiki/TcHWwg3Tgiqotqkp7u4clnMLn5e\n--From Test-Server"

    if final_msg.strip():
        if status == 1:
            fsm.sendTextmessage(final_msg)
        elif status == 2:
            fst.sendTextmessage(final_msg)
            fsdev.sendTextmessage(final_msg)

    # 保存报告到文件（使用cm.json_dir()）
    report_txt_path = os.path.join(cm.json_dir(), "report.txt")
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write(final_msg)
    logger.log("INFO", f"报告已保存到: {report_txt_path}")

def main():
    try:
        status = 1
        test_file = None
        case_mark = None

        # 解析命令行参数
        if len(sys.argv) > 1:
            status = int(sys.argv[1])
        if len(sys.argv) > 2:
            arg2 = sys.argv[2]
            # 用例标记直接判断字符串（如果需要在cm中统一管理，可在ConfigManager中添加）
            if arg2 in ["main", "other"]:
                case_mark = arg2
            else:
                test_file = arg2

        # 执行流程
        delete_report_file()
        execute_test_steps(test_file, case_mark)
        terminate_java_process()

        # 报告处理
        temp_dict = {
            'test_main_case': '主流程：OFF折扣支付验证',
            'test_other_case': '非主流程：会员充值验证'
        }
        temp_dict_en = {
            'test_main_case': 'Main: OFF Discount Payment',
            'test_other_case': 'Other: Member Recharge'
        }

        results = read_test_report()
        if results:
            passed, failed, failed_details = classify_test_results(results)
            send_test_report(passed, failed, temp_dict, temp_dict_en, failed_details, status)
            fsm.sendTextmessage("测试报告已发送")
        else:
            logger.log("WARNING", "未读取到测试报告，跳过报告发送")

    except Exception as e:
        error_msg = f"测试执行失败: {str(e)}"
        logger.log("ERROR", error_msg)
        fsm.sendTextmessage(error_msg)

if __name__ == "__main__":
    main()