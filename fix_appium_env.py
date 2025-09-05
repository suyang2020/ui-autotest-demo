#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Appium环境修复脚本
用于解决UiAutomator2 instrumentation进程崩溃问题
"""
import sys
import subprocess
import time
from pathlib import Path
from src.utils import get_logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


logger = get_logger(__name__)


def check_adb_devices():
    """检查ADB设备连接状态"""
    print("📱 检查ADB设备连接状态...")
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
        print(f"ADB设备列表:\n{result.stdout}")
        
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
        devices = [line for line in lines if line.strip() and '\tdevice' in line]
        
        if devices:
            print(f"✅ 找到 {len(devices)} 个设备:")
            for device in devices:
                print(f"   - {device}")
            return True
        else:
            print("❌ 没有找到连接的设备")
            return False
    except Exception as e:
        print(f"❌ 检查ADB设备失败: {e}")
        return False


def kill_appium_processes():
    """杀死所有Appium相关进程"""
    print("🔄 停止所有Appium相关进程...")
    
    # Windows平台的进程名
    processes_to_kill = [
        'appium',
        'node.exe',  # Appium通常运行在Node.js上
        'adb.exe'
    ]
    
    for process_name in processes_to_kill:
        try:
            # 使用taskkill命令强制终止进程
            result = subprocess.run(['taskkill', '/F', '/IM', process_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ 已停止 {process_name}")
            else:
                print(f"   ℹ️  {process_name} 未运行或已停止")
        except Exception as e:
            print(f"   ⚠️  停止 {process_name} 时出错: {e}")


def restart_adb():
    """重启ADB服务"""
    print("🔄 重启ADB服务...")
    try:
        # 停止ADB服务
        subprocess.run(['adb', 'kill-server'], capture_output=True, timeout=10)
        print("   ✅ ADB服务已停止")
        
        time.sleep(2)
        
        # 启动ADB服务
        result = subprocess.run(['adb', 'start-server'], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("   ✅ ADB服务已重启")
            return True
        else:
            print(f"   ❌ ADB服务重启失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 重启ADB服务失败: {e}")
        return False


def clear_app_data():
    """清理应用数据（如果知道包名）"""
    print("🧹 清理应用数据...")
    
    # 这里需要根据实际的应用包名进行调整
    app_packages = [
        'io.appium.uiautomator2.server',
        'io.appium.uiautomator2.server.test',
        'io.appium.settings'
    ]
    
    for package in app_packages:
        try:
            # 清理应用数据
            result = subprocess.run(['adb', 'shell', 'pm', 'clear', package], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ 已清理 {package}")
            else:
                print(f"   ℹ️  {package} 清理失败或不存在")
        except Exception as e:
            print(f"   ⚠️  清理 {package} 时出错: {e}")


def start_appium_server():
    """启动Appium服务器"""
    print("🚀 启动Appium服务器...")
    try:
        # 启动Appium服务器
        appium_cmd = [
            'appium',
            '--port', '4723',
            '--session-override',  # 允许覆盖现有会话
            '--log-level', 'info'
        ]
        
        print(f"   执行命令: {' '.join(appium_cmd)}")
        
        # 启动后台进程
        process = subprocess.Popen(appium_cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        
        # 等待几秒看服务器是否正常启动
        time.sleep(5)
        
        if process.poll() is None:  # 进程仍在运行
            print("   ✅ Appium服务器启动成功")
            return True, process
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ Appium服务器启动失败")
            print(f"   输出: {stdout}")
            print(f"   错误: {stderr}")
            return False, None
    except Exception as e:
        print(f"❌ 启动Appium服务器失败: {e}")
        return False, None


def test_appium_connection():
    """测试Appium连接"""
    print("🧪 测试Appium连接...")
    try:
        # 简单的HTTP请求测试Appium服务器
        import requests
        response = requests.get('http://localhost:4723/status', timeout=10)
        if response.status_code == 200:
            print("   ✅ Appium服务器响应正常")
            return True
        else:
            print(f"   ❌ Appium服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试Appium连接失败: {e}")
        return False


def quick_driver_test():
    """快速驱动测试"""
    print("🔧 快速驱动创建测试...")
    try:
        from src.core.driver_manager import DriverFactory
        
        print("   正在创建测试驱动...")
        driver = DriverFactory.create_android_driver()
        print("   ✅ 驱动创建成功!")
        
        # 获取一些基本信息
        current_activity = driver.current_activity
        print(f"   当前Activity: {current_activity}")
        
        driver.quit()
        print("   ✅ 驱动已正常关闭")
        return True
        
    except Exception as e:
        print(f"❌ 驱动测试失败: {e}")
        return False


def main():
    """主修复流程"""
    print("=" * 60)
    print("🔧 Appium环境修复脚本")
    print("=" * 60)
    
    # 1. 检查设备连接
    if not check_adb_devices():
        print("\\n⚠️  请确保Android设备已连接并启用USB调试")
        return False
    
    # 2. 停止所有相关进程
    kill_appium_processes()
    
    # 3. 重启ADB
    if not restart_adb():
        print("\\n❌ ADB重启失败，请手动检查")
        return False
    
    # 4. 再次检查设备
    time.sleep(2)
    if not check_adb_devices():
        print("\\n❌ 重启ADB后设备仍未连接")
        return False
    
    # 5. 清理应用数据
    clear_app_data()
    
    # 6. 启动Appium服务器
    success, appium_process = start_appium_server()
    if not success:
        print("\\n❌ Appium服务器启动失败")
        return False
    
    # 7. 测试连接
    time.sleep(3)
    if not test_appium_connection():
        print("\\n❌ Appium连接测试失败")
        if appium_process:
            appium_process.terminate()
        return False
    
    # 8. 快速驱动测试
    if quick_driver_test():
        print("\\n🎉 环境修复成功！")
        print("\\n📝 建议:")
        print("   1. 保持Appium服务器运行")
        print("   2. 现在可以运行测试: python run_tests.py login")
        
        # 保持Appium服务器运行
        try:
            print("\\n⏳ Appium服务器将保持运行，按Ctrl+C停止...")
            appium_process.wait()
        except KeyboardInterrupt:
            print("\\n🛑 正在停止Appium服务器...")
            appium_process.terminate()
            appium_process.wait()
            print("✅ Appium服务器已停止")
        
        return True
    else:
        print("\\n❌ 驱动测试失败，环境仍有问题")
        if appium_process:
            appium_process.terminate()
        return False


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\\n❌ 环境修复失败，请检查以下内容:")
            print("   1. Android设备是否正确连接")
            print("   2. USB调试是否已启用")
            print("   3. Appium和Node.js是否正确安装")
            print("   4. 设备是否需要重新授权")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\\n🛑 修复过程被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\\n💥 修复过程出现异常: {e}")
        sys.exit(1)