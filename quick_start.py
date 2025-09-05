#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速开始示例脚本
演示如何使用ui-autotest框架
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.core import DriverFactory, driver_manager
from src.pages.page_factory import PageFactory
from src.pages.app import LoginPage, HomePage
from src.utils import get_logger, take_screenshot

logger = get_logger(__name__)


def quick_start_demo():
    """快速开始演示"""
    
    print("🚀 UI自动化测试框架 - 快速开始演示")
    print("=" * 50)
    
    driver = None
    
    try:
        # 1. 检查配置
        print("📋 1. 检查配置...")
        print(f"   Appium服务器: {config.get('appium.server_url')}")
        print(f"   测试超时: {config.get('test.default_timeout')}秒")
        print(f"   截图目录: {config.get('test.screenshot_dir')}")
        
        # 2. 创建WebDriver（这里只是演示，实际可能需要真实设备）
        print("\\n🔌 2. 创建WebDriver...")
        print("   注意: 这需要Appium服务器运行且有可用设备")
        print("   如果没有设备，这一步会失败，但不影响演示其他功能")
        
        try:
            driver = DriverFactory.create_android_driver()
            print("   ✅ WebDriver创建成功")
        except Exception as e:
            print(f"   ❌ WebDriver创建失败: {e}")
            print("   💡 提示: 请确保Appium服务器运行且有可用设备")
            print("   继续演示其他功能...")
        
        # 3. 创建页面对象
        print("\\n📱 3. 创建页面对象...")
        login_page = PageFactory.create_page("login_page", driver)
        home_page = PageFactory.create_page("home_page", driver)
        print("   ✅ 页面对象创建成功")
        print(f"   - 登录页面: {login_page.__class__.__name__}")
        print(f"   - 主页面: {home_page.__class__.__name__}")
        
        # 4. 演示配置系统
        print("\\n⚙️ 4. 配置系统演示...")
        android_config = config.get_device_config('android')
        print(f"   平台: {android_config.get('platformName')}")
        print(f"   自动化引擎: {android_config.get('automationName')}")
        print(f"   设备名称: {android_config.get('deviceName')}")
        
        # 5. 演示工具功能
        print("\\n🛠️ 5. 工具功能演示...")
        
        # 截图功能（如果有driver）
        if driver:
            try:
                screenshot_path = take_screenshot("demo_screenshot")
                print(f"   ✅ 截图功能: {screenshot_path}")
            except Exception as e:
                print(f"   ⚠️ 截图功能: {e}")
        else:
            print("   📷 截图功能: 需要WebDriver实例")
        
        # 数据生成器
        from src.utils import generate_user_data
        test_user = generate_user_data("normal")
        print(f"   🎲 随机用户数据: {test_user['username']} / {test_user['email']}")
        
        # 6. 演示页面对象方法
        print("\\n📄 6. 页面对象方法演示...")
        print("   登录页面方法:")
        methods = [method for method in dir(login_page) if not method.startswith('_') and callable(getattr(login_page, method))]
        for method in methods[:5]:  # 只显示前5个方法
            print(f"     - {method}()")
        print(f"     ... 总共 {len(methods)} 个方法")
        
        # 7. 演示断言功能
        print("\\n✅ 7. 断言功能演示...")
        from src.utils import assert_equal, assert_true
        try:
            assert_equal(1, 1, "数字相等断言")
            assert_true(True, "布尔值断言")
            print("   ✅ 断言测试通过")
        except Exception as e:
            print(f"   ❌ 断言测试失败: {e}")
        
        # 8. 演示报告功能
        print("\\n📊 8. 报告功能演示...")
        from src.utils.report_manager import allure_manager
        print(f"   Allure结果目录: {allure_manager.results_dir}")
        print(f"   Allure报告目录: {allure_manager.report_dir}")
        
        print("\\n🎉 演示完成！")
        print("\\n📚 下一步:")
        print("   1. 配置你的设备信息在 config.yaml")
        print("   2. 启动Appium服务器")
        print("   3. 运行: python run_tests.py check")
        print("   4. 运行: python run_tests.py smoke")
        
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        print(f"\\n❌ 演示失败: {e}")
    
    finally:
        # 清理
        if driver:
            try:
                driver_manager.quit_all_drivers()
                print("\\n🧹 WebDriver已清理")
            except Exception as e:
                print(f"\\n⚠️ WebDriver清理时出错: {e}")


def show_project_structure():
    """显示项目结构"""
    print("\\n📁 项目结构:")
    print("""
ui-autotest/
├── src/                     # 源代码目录
│   ├── config/             # 配置管理
│   ├── core/               # 核心功能
│   ├── pages/              # 页面对象
│   ├── tests/              # 测试用例
│   └── utils/              # 工具类
├── reports/                # 测试报告
├── logs/                   # 日志文件
├── config.yaml            # 配置文件
├── run_tests.py           # 测试运行脚本
└── README.md              # 项目文档
    """)


def show_available_commands():
    """显示可用命令"""
    print("\\n💻 可用命令:")
    commands = [
        ("python run_tests.py check", "检查测试环境"),
        ("python run_tests.py smoke", "运行冒烟测试"),
        ("python run_tests.py regression", "运行回归测试"),
        ("python run_tests.py login", "运行登录测试"),
        ("python run_tests.py home", "运行主页测试"),
        ("python run_tests.py report", "生成测试报告"),
        ("python run_tests.py clean", "清理测试报告"),
        ("python quick_start.py", "运行快速演示"),
    ]
    
    for cmd, desc in commands:
        print(f"   {cmd:<30} - {desc}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="UI自动化测试框架快速开始")
    parser.add_argument("--demo", action="store_true", help="运行完整演示")
    parser.add_argument("--structure", action="store_true", help="显示项目结构")
    parser.add_argument("--commands", action="store_true", help="显示可用命令")
    
    args = parser.parse_args()
    
    if args.structure:
        show_project_structure()
    elif args.commands:
        show_available_commands()
    elif args.demo or len(sys.argv) == 1:
        quick_start_demo()
        show_project_structure()
        show_available_commands()
    else:
        parser.print_help()