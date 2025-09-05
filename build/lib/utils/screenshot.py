"""
截图工具模块
提供截图功能，支持失败时自动截图
"""
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from appium.webdriver.webdriver import WebDriver
from .logger import get_logger
from ..config import config
from ..core import driver_manager

logger = get_logger(__name__)


class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, driver: WebDriver = None):
        self.driver = driver or driver_manager.get_driver()
        self.screenshot_dir = Path(config.get_test_config().get('screenshot_dir', './reports/screenshots'))
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def take_screenshot(self, filename: str = None, description: str = None) -> str:
        """截图"""
        if not self.driver:
            logger.warning("无WebDriver实例，无法截图")
            return ""
        
        try:
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                filename = f"screenshot_{timestamp}.png"
            
            # 确保文件名以.png结尾
            if not filename.endswith('.png'):
                filename += '.png'
            
            # 保存截图
            filepath = self.screenshot_dir / filename
            self.driver.save_screenshot(str(filepath))
            
            logger.info(f"截图保存成功: {filepath}")
            
            # 如果有Allure，添加附件
            self._attach_to_allure(filepath, description or "截图")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return ""
    
    def take_failure_screenshot(self, test_name: str = None) -> str:
        """失败时截图"""
        test_name = test_name or "failed_test"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"FAILED_{test_name}_{timestamp}.png"
        
        return self.take_screenshot(filename, f"测试失败截图: {test_name}")
    
    def take_step_screenshot(self, step_name: str) -> str:
        """步骤截图"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_step_name = "".join(c for c in step_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"step_{safe_step_name}_{timestamp}.png"
        
        return self.take_screenshot(filename, f"步骤截图: {step_name}")
    
    def _attach_to_allure(self, filepath: Path, description: str):
        """添加到Allure报告"""
        try:
            import allure
            with open(filepath, 'rb') as f:
                allure.attach(f.read(), name=description, attachment_type=allure.attachment_type.PNG)
        except ImportError:
            pass  # Allure未安装时忽略
        except Exception as e:
            logger.debug(f"添加Allure附件失败: {e}")
    
    def cleanup_old_screenshots(self, days: int = 7):
        """清理旧截图"""
        try:
            current_time = time.time()
            for screenshot_file in self.screenshot_dir.glob("*.png"):
                file_time = screenshot_file.stat().st_mtime
                if current_time - file_time > days * 24 * 3600:
                    screenshot_file.unlink()
                    logger.debug(f"删除旧截图: {screenshot_file}")
        except Exception as e:
            logger.warning(f"清理旧截图失败: {e}")


class ScreenshotDecorator:
    """截图装饰器"""
    
    @staticmethod
    def screenshot_on_failure(func):
        """失败时自动截图的装饰器"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 尝试获取测试名称
                test_name = getattr(func, '__name__', 'unknown_test')
                
                # 截图
                screenshot_manager = ScreenshotManager()
                screenshot_path = screenshot_manager.take_failure_screenshot(test_name)
                
                if screenshot_path:
                    logger.error(f"测试失败，已截图: {screenshot_path}")
                
                raise
        
        return wrapper
    
    @staticmethod
    def screenshot_before_after(func):
        """执行前后都截图的装饰器"""
        def wrapper(*args, **kwargs):
            test_name = getattr(func, '__name__', 'unknown_test')
            screenshot_manager = ScreenshotManager()
            
            # 执行前截图
            screenshot_manager.take_step_screenshot(f"{test_name}_before")
            
            try:
                result = func(*args, **kwargs)
                # 执行后截图
                screenshot_manager.take_step_screenshot(f"{test_name}_after")
                return result
            except Exception as e:
                # 失败时截图
                screenshot_manager.take_failure_screenshot(test_name)
                raise
        
        return wrapper


# 全局截图管理器实例
screenshot_manager = ScreenshotManager()


# 便捷函数
def take_screenshot(filename: str = None, description: str = None) -> str:
    """截图的便捷函数"""
    return screenshot_manager.take_screenshot(filename, description)


def take_failure_screenshot(test_name: str = None) -> str:
    """失败截图的便捷函数"""
    return screenshot_manager.take_failure_screenshot(test_name)


def take_step_screenshot(step_name: str) -> str:
    """步骤截图的便捷函数"""
    return screenshot_manager.take_step_screenshot(step_name)