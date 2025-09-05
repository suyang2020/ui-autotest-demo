"""
Appium驱动管理模块
负责WebDriver的创建、管理和销毁
"""
import atexit
from typing import Optional, Dict, Any
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from ..config import config, env_manager
import logging

logger = logging.getLogger(__name__)


class DriverManager:
    """驱动管理器，使用单例模式"""
    
    _instance = None
    _drivers: Dict[str, WebDriver] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DriverManager, cls).__new__(cls)
            # 注册退出处理函数
            atexit.register(cls._instance.quit_all_drivers)
        return cls._instance
    
    def create_driver(self, platform: str = 'android', driver_name: str = 'default') -> WebDriver:
        """创建WebDriver实例"""
        try:
            # 获取配置
            appium_config = config.get_appium_config()
            device_config = config.get_device_config(platform)
            
            # 合并配置
            capabilities = device_config.copy()
            
            # 环境相关配置调整
            if env_manager.is_development():
                capabilities['newCommandTimeout'] = capabilities.get('newCommandTimeout', 300)
            
            # 创建WebDriver
            server_url = appium_config.get('server_url', 'http://localhost:4723/wd/hub')
            driver = webdriver.Remote(server_url, capabilities)
            
            # 设置隐式等待
            timeout = config.get_test_config().get('implicit_wait', 5)
            driver.implicitly_wait(timeout)
            
            # 存储驱动实例
            self._drivers[driver_name] = driver
            
            logger.info(f"成功创建 {platform} 驱动: {driver_name}")
            return driver
            
        except Exception as e:
            logger.error(f"创建驱动失败: {e}")
            raise WebDriverException(f"无法创建WebDriver: {e}")
    
    def get_driver(self, driver_name: str = 'default') -> Optional[WebDriver]:
        """获取WebDriver实例"""
        return self._drivers.get(driver_name)
    
    def quit_driver(self, driver_name: str = 'default'):
        """退出指定驱动"""
        if driver_name in self._drivers:
            try:
                self._drivers[driver_name].quit()
                logger.info(f"已退出驱动: {driver_name}")
            except Exception as e:
                logger.warning(f"退出驱动时出错: {e}")
            finally:
                del self._drivers[driver_name]
    
    def quit_all_drivers(self):
        """退出所有驱动"""
        driver_names = list(self._drivers.keys())
        for driver_name in driver_names:
            self.quit_driver(driver_name)
    
    def restart_driver(self, driver_name: str = 'default', platform: str = 'android') -> WebDriver:
        """重启驱动"""
        self.quit_driver(driver_name)
        return self.create_driver(platform, driver_name)
    
    def is_driver_alive(self, driver_name: str = 'default') -> bool:
        """检查驱动是否存活"""
        driver = self.get_driver(driver_name)
        if driver is None:
            return False
        
        try:
            # 尝试获取当前窗口句柄来测试连接
            driver.current_window_handle
            return True
        except Exception:
            return False


class DriverFactory:
    """驱动工厂类"""
    
    @staticmethod
    def create_android_driver(device_name: str = None, app_path: str = None, 
                            package_name: str = None, activity: str = None) -> WebDriver:
        """创建Android驱动"""
        manager = DriverManager()
        
        # 动态更新配置
        if device_name:
            config.update_config('devices.android.deviceName', device_name)
        if app_path:
            config.update_config('devices.android.app', app_path)
        if package_name:
            config.update_config('devices.android.appPackage', package_name)
        if activity:
            config.update_config('devices.android.appActivity', activity)
        
        return manager.create_driver('android')
    
    @staticmethod
    def create_ios_driver(device_name: str = None, app_path: str = None, 
                         bundle_id: str = None) -> WebDriver:
        """创建iOS驱动"""
        manager = DriverManager()
        
        # 动态更新配置
        if device_name:
            config.update_config('devices.ios.deviceName', device_name)
        if app_path:
            config.update_config('devices.ios.app', app_path)
        if bundle_id:
            config.update_config('devices.ios.bundleId', bundle_id)
        
        return manager.create_driver('ios')


# 全局驱动管理器实例
driver_manager = DriverManager()