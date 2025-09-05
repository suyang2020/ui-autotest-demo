#!/usr/bin/env python3
"""
获取应用页面元素信息的脚本
用于帮助配置页面对象中的元素定位器
"""

import time
import json
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from src.config.config import Config


def get_page_source_and_elements():
    """获取当前页面的源码和元素信息"""
    
    # 加载配置
    config = Config()
    device_config = config.get_device_config("android")
    
    print("正在连接设备和启动应用...")
    print(f"设备: {device_config['deviceName']}")
    print(f"应用包名: {device_config['appPackage']}")
    print(f"应用Activity: {device_config['appActivity']}")
    
    # 创建驱动
    from appium.options.android import UiAutomator2Options
    
    options = UiAutomator2Options()
    for key, value in device_config.items():
        setattr(options, key, value)
    
    appium_config = config.get_appium_config()
    driver = webdriver.Remote(
        command_executor=appium_config.get('server_url', 'http://localhost:4723'),
        options=options
    )
    
    try:
        print("\n等待应用启动...")
        time.sleep(5)
        
        # 获取当前页面源码
        page_source = driver.page_source
        
        # 保存页面源码到文件
        with open("page_source.xml", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("页面源码已保存到 page_source.xml")
        
        # 获取所有可见元素
        print("\n=== 获取页面元素信息 ===")
        
        # 尝试查找常见的登录相关元素
        login_elements = {}
        
        # 查找输入框
        input_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        if input_elements:
            print(f"\n找到 {len(input_elements)} 个输入框:")
            for i, element in enumerate(input_elements):
                resource_id = element.get_attribute("resource-id")
                text = element.get_attribute("text")
                hint = element.get_attribute("hint")
                content_desc = element.get_attribute("content-desc")
                
                print(f"  输入框 {i+1}:")
                print(f"    resource-id: {resource_id}")
                print(f"    text: {text}")
                print(f"    hint: {hint}")
                print(f"    content-desc: {content_desc}")
                
                # 根据内容推测用途
                if hint and ("用户" in hint or "账号" in hint or "手机" in hint or "邮箱" in hint):
                    login_elements["username_input"] = resource_id
                elif hint and ("密码" in hint or "口令" in hint):
                    login_elements["password_input"] = resource_id
        
        # 查找按钮
        button_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
        if button_elements:
            print(f"\n找到 {len(button_elements)} 个按钮:")
            for i, element in enumerate(button_elements):
                resource_id = element.get_attribute("resource-id")
                text = element.get_attribute("text")
                content_desc = element.get_attribute("content-desc")
                
                print(f"  按钮 {i+1}:")
                print(f"    resource-id: {resource_id}")
                print(f"    text: {text}")
                print(f"    content-desc: {content_desc}")
                
                # 根据内容推测用途
                if text and ("登录" in text or "登陆" in text or "signin" in text.lower()):
                    login_elements["login_button"] = resource_id
                elif text and ("注册" in text or "signup" in text.lower()):
                    login_elements["register_button"] = resource_id
        
        # 查找文本视图（可能包含错误信息）
        text_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        if text_elements:
            print(f"\n找到 {len(text_elements)} 个文本元素:")
            for i, element in enumerate(text_elements[:10]):  # 只显示前10个
                resource_id = element.get_attribute("resource-id")
                text = element.get_attribute("text")
                
                if text and len(text.strip()) > 0:  # 只显示有文本的元素
                    print(f"  文本 {i+1}:")
                    print(f"    resource-id: {resource_id}")
                    print(f"    text: {text}")
        
        # 查找图片按钮
        image_button_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.ImageButton")
        if image_button_elements:
            print(f"\n找到 {len(image_button_elements)} 个图片按钮:")
            for i, element in enumerate(image_button_elements):
                resource_id = element.get_attribute("resource-id")
                content_desc = element.get_attribute("content-desc")
                
                print(f"  图片按钮 {i+1}:")
                print(f"    resource-id: {resource_id}")
                print(f"    content-desc: {content_desc}")
        
        # 保存推测的登录元素
        if login_elements:
            print(f"\n=== 推测的登录相关元素 ===")
            for key, value in login_elements.items():
                print(f"{key}: {value}")
            
            with open("login_elements.json", "w", encoding="utf-8") as f:
                json.dump(login_elements, f, ensure_ascii=False, indent=2)
            print("登录元素信息已保存到 login_elements.json")
        
        # 生成建议的页面对象代码
        print(f"\n=== 建议的页面对象元素定位器代码 ===")
        if login_elements:
            for key, resource_id in login_elements.items():
                if resource_id:
                    print(f'{key.upper()} = ElementLocators.android_id("{resource_id}")')
                else:
                    print(f'{key.upper()} = # 需要手动设置定位器')
        
    except Exception as e:
        print(f"获取元素信息时发生错误: {e}")
        
    finally:
        print("\n关闭应用...")
        driver.quit()


if __name__ == "__main__":
    get_page_source_and_elements()