#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toast调试脚本
专门用于调试Toast获取问题
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core import driver_manager
from src.pages.page_factory import PageFactory
from src.utils import get_logger
from appium.webdriver.common.appiumby import AppiumBy

logger = get_logger(__name__)


def debug_toast_capture():
    """调试Toast捕获功能"""
    
    # 创建驱动
    driver = driver_manager.create_driver(platform='android')
    
    try:
        # 创建登录页面实例
        login_page = PageFactory.create_page("login_page", driver)
        
        print("=== Toast调试会话开始 ===")
        
        # 等待登录页面加载
        print("1. 等待登录页面加载...")
        login_page.wait_for_page_load()
        
        # 输入无效手机号
        print("2. 输入无效手机号...")
        login_page.enter_phone_number("1321000100")
        
        print("3. 准备点击获取验证码按钮...")
        print("   正在监控页面源码变化...")
        
        # 获取点击前的页面源码（用于对比）
        before_source = driver.page_source
        print(f"   点击前页面源码长度: {len(before_source)}")
        
        # 点击获取验证码
        print("4. 点击获取验证码按钮...")
        login_page.click_get_verification_code()
        
        # 立即开始多轮Toast检测
        print("5. 开始Toast检测...")
        
        for attempt in range(1, 11):  # 10次尝试，每次0.5秒
            print(f"   尝试 {attempt}/10...")
            
            # 方法1：检查页面源码是否包含Toast相关文本
            current_source = driver.page_source
            toast_keywords = ["toast", "Toast", "请输入", "格式", "手机号", "验证码"]
            
            for keyword in toast_keywords:
                if keyword in current_source and keyword not in before_source:
                    print(f"   ✓ 在页面源码中发现新的关键词: {keyword}")
            
            # 方法2：尝试多种Toast定位器
            toast_selectors = [
                "//android.widget.Toast",
                "//android.widget.Toast[@text]",
                "//*[contains(@class, 'Toast')]",
                "//*[contains(@resource-id, 'toast')]",
                "//*[contains(text(), '请输入')]",
                "//*[contains(text(), '格式')]",
                "//*[contains(text(), '手机号')]",
                "//*[contains(text(), '验证码')]"
            ]
            
            found_elements = []
            for selector in toast_selectors:
                try:
                    elements = driver.find_elements(AppiumBy.XPATH, selector)
                    if elements:
                        for elem in elements:
                            try:
                                text_content = elem.get_attribute("text") or elem.text or elem.get_attribute("name")
                                if text_content:
                                    found_elements.append({
                                        'selector': selector,
                                        'text': text_content,
                                        'bounds': elem.get_attribute("bounds"),
                                        'displayed': elem.is_displayed()
                                    })
                            except:
                                pass
                except:
                    pass
            
            if found_elements:
                print(f"   ✓ 找到 {len(found_elements)} 个可能的Toast元素:")
                for elem in found_elements:
                    print(f"      - 选择器: {elem['selector']}")
                    print(f"        文本: {elem['text']}")
                    print(f"        边界: {elem['bounds']}")
                    print(f"        可见: {elem['displayed']}")
                    print()
                break
            else:
                print(f"   ✗ 第{attempt}次未找到Toast元素")
            
            time.sleep(0.5)
        
        # 方法3：使用基础页面的Toast获取方法
        print("6. 使用基础Toast获取方法...")
        toast_message = login_page.get_toast_message(timeout=3)
        if toast_message:
            print(f"   ✓ 基础方法获取到Toast: {toast_message}")
        else:
            print("   ✗ 基础方法未获取到Toast")
        
        # 方法4：获取页面上所有文本元素
        print("7. 扫描页面上所有文本元素...")
        text_selectors = [
            "//android.widget.TextView",
            "//android.view.View[@text]",
            "//android.widget.EditText",
            "//*[@text]"
        ]
        
        all_texts = set()
        for selector in text_selectors:
            try:
                elements = driver.find_elements(AppiumBy.XPATH, selector)
                for elem in elements:
                    try:
                        text = elem.get_attribute("text") or elem.text
                        if text and len(text.strip()) > 0:
                            all_texts.add(text.strip())
                    except:
                        pass
            except:
                pass
        
        print(f"   找到 {len(all_texts)} 个文本元素:")
        for text in sorted(all_texts):
            if any(keyword in text for keyword in ["请输入", "格式", "手机号", "验证码", "错误"]):
                print(f"      ⭐ {text}")
            else:
                print(f"         {text}")
        
        print("\n8. 尝试登录按钮...")
        login_page.click_login_button()
        
        print("9. 再次检测Toast...")
        time.sleep(1)
        
        toast_message2 = login_page.get_toast_message(timeout=3)
        if toast_message2:
            print(f"   ✓ 登录后获取到Toast: {toast_message2}")
        else:
            print("   ✗ 登录后未获取到Toast")
        
        print("\n=== Toast调试会话结束 ===")
        
    except Exception as e:
        logger.error(f"调试过程中出错: {e}")
        print(f"调试失败: {e}")
        
    finally:
        # 清理资源
        print("清理测试环境...")
        driver_manager.quit_driver()


if __name__ == "__main__":
    print("开始Toast调试...")
    debug_toast_capture()
    print("调试结束")