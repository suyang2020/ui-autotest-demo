#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
提供各种测试执行选项和批量运行功能
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config, env_manager
from src.config.environment import Environment
from src.core import appium_server_manager
from src.utils import get_logger, generate_reports
from src.utils.report_manager import allure_manager

logger = get_logger(__name__)


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_tests(self, test_path: str = None, markers: List[str] = None, 
                  platform: str = "android", device: str = None, 
                  app: str = None, env: str = "test", 
                  parallel: int = 1, verbose: bool = False) -> bool:
        """运行测试"""
        
        # 设置环境
        if env:
            os.environ['TEST_ENV'] = env
            env_manager.set_environment(Environment(env))
        
        # 构建pytest命令
        cmd = ["python", "-m", "pytest"]
        
        # 测试路径
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append("src/tests/")
        
        # 标记过滤
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # 平台参数
        cmd.extend(["--platform", platform])
        
        # 设备参数
        if device:
            cmd.extend(["--device", device])
        
        # 应用参数
        if app:
            cmd.extend(["--app", app])
        
        # 环境参数
        cmd.extend(["--env", env])
        
        # 并行执行
        if parallel > 1:
            cmd.extend(["-n", str(parallel)])
        
        # 详细输出
        if verbose:
            cmd.append("-v")
        
        # Allure报告配置
        cmd.extend(["--alluredir", str(allure_manager.results_dir)])
        cmd.append("--clean-alluredir")  # 清空之前的结果
        
        # 其他选项
        cmd.extend([
            "--tb=short",  # 简短的错误回溯
            "--strict-markers",  # 严格标记模式
        ])
        
        logger.info(f"执行测试命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"运行测试失败: {e}")
            return False
    
    def run_smoke_tests(self, platform: str = "android") -> bool:
        """运行冒烟测试"""
        logger.info("开始执行冒烟测试")
        return self.run_tests(markers=["smoke"], platform=platform, verbose=True)
    
    def run_regression_tests(self, platform: str = "android") -> bool:
        """运行回归测试"""
        logger.info("开始执行回归测试")
        return self.run_tests(markers=["regression"], platform=platform)
    
    def run_login_tests(self, platform: str = "android") -> bool:
        """运行登录相关测试"""
        logger.info("开始执行登录测试")
        return self.run_tests(test_path="src/tests/app/test_login.py", platform=platform, verbose=True)
    
    def run_home_tests(self, platform: str = "android") -> bool:
        """运行主页相关测试"""
        logger.info("开始执行主页测试")
        return self.run_tests(test_path="src/tests/app/test_home.py", platform=platform, verbose=True)
    
    def generate_and_open_report(self, open_browser: bool = True) -> bool:
        """生成并打开测试报告"""
        logger.info("生成测试报告")
        allure_success, html_success = generate_reports(open_browser=open_browser)
        
        if allure_success:
            logger.info("Allure报告生成成功")
        else:
            logger.error("Allure报告生成失败")
        
        return allure_success
    
    def cleanup_reports(self):
        """清理旧的测试报告"""
        logger.info("清理旧的测试报告")
        allure_manager.clean_results()
    
    def check_environment(self) -> bool:
        """检查测试环境"""
        logger.info("检查测试环境")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            logger.error("Python版本需要3.8或更高")
            return False
        
        # 检查依赖包
        required_packages = [
            ("pytest", "pytest"), 
            ("allure-pytest", "allure_pytest"), 
            ("selenium", "selenium"),
            ("appium-python-client", "appium"), 
            ("requests", "requests")
        ]
        
        missing_packages = []
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(package_name)
        
        if missing_packages:
            logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.info("请运行: pip install -r requirements.txt")
            return False
        
        # 检查Allure命令行工具
        commands_to_try = ['allure', 'allure.bat']
        allure_found = False
        
        for cmd in commands_to_try:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, 
                                      timeout=10, shell=True)
                if result.returncode == 0:
                    logger.info(f"Allure命令行工具已安装: {cmd}, 版本: {result.stdout.strip()}")
                    allure_found = True
                    break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        if not allure_found:
            logger.warning("未找到Allure命令行工具，报告生成可能失败")
        
        # 检查Appium服务器
        if appium_server_manager.server.is_running():
            logger.info("Appium服务器正在运行")
        else:
            logger.warning("Appium服务器未运行，将尝试自动启动")
        
        logger.info("环境检查完成")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="UI自动化测试运行脚本")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 运行测试命令
    run_parser = subparsers.add_parser("run", help="运行测试")
    run_parser.add_argument("--path", help="测试路径")
    run_parser.add_argument("--markers", nargs="+", help="测试标记")
    run_parser.add_argument("--platform", default="android", choices=["android", "ios"], help="测试平台")
    run_parser.add_argument("--device", help="设备名称")
    run_parser.add_argument("--app", help="应用路径")
    run_parser.add_argument("--env", default="test", choices=["dev", "test", "staging", "prod"], help="测试环境")
    run_parser.add_argument("--parallel", type=int, default=1, help="并行数量")
    run_parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    # 冒烟测试命令
    smoke_parser = subparsers.add_parser("smoke", help="运行冒烟测试")
    smoke_parser.add_argument("--platform", default="android", choices=["android", "ios"], help="测试平台")
    
    # 回归测试命令
    regression_parser = subparsers.add_parser("regression", help="运行回归测试")
    regression_parser.add_argument("--platform", default="android", choices=["android", "ios"], help="测试平台")
    
    # 登录测试命令
    login_parser = subparsers.add_parser("login", help="运行登录测试")
    login_parser.add_argument("--platform", default="android", choices=["android", "ios"], help="测试平台")
    
    # 主页测试命令
    home_parser = subparsers.add_parser("home", help="运行主页测试")
    home_parser.add_argument("--platform", default="android", choices=["android", "ios"], help="测试平台")
    
    # 报告命令
    report_parser = subparsers.add_parser("report", help="生成测试报告")
    report_parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    
    # 清理命令
    clean_parser = subparsers.add_parser("clean", help="清理测试报告")
    
    # 环境检查命令
    check_parser = subparsers.add_parser("check", help="检查测试环境")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    runner = TestRunner()
    
    try:
        if args.command == "run":
            success = runner.run_tests(
                test_path=args.path,
                markers=args.markers,
                platform=args.platform,
                device=args.device,
                app=args.app,
                env=args.env,
                parallel=args.parallel,
                verbose=args.verbose
            )
            if success:
                runner.generate_and_open_report(not args.verbose)
        
        elif args.command == "smoke":
            success = runner.run_smoke_tests(args.platform)
            if success:
                runner.generate_and_open_report()
        
        elif args.command == "regression":
            success = runner.run_regression_tests(args.platform)
            if success:
                runner.generate_and_open_report()
        
        elif args.command == "login":
            success = runner.run_login_tests(args.platform)
            # 强制生成报告，不论测试是否成功
            logger.info("开始生成Allure报告...")
            runner.generate_and_open_report()
        
        elif args.command == "home":
            success = runner.run_home_tests(args.platform)
            if success:
                runner.generate_and_open_report()
        
        elif args.command == "report":
            runner.generate_and_open_report(not args.no_open)
        
        elif args.command == "clean":
            runner.cleanup_reports()
        
        elif args.command == "check":
            runner.check_environment()
    
    except KeyboardInterrupt:
        logger.info("测试执行被用户中断")
    except Exception as e:
        logger.error(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()