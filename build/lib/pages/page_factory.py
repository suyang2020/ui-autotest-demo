"""
页面工厂模块
用于创建和管理页面对象实例
"""
from typing import Type, Dict, Any
from appium.webdriver.webdriver import WebDriver
from .base_page import BasePage
from ..core import driver_manager
import logging

logger = logging.getLogger(__name__)


class PageFactory:
    """页面工厂类"""
    
    _page_registry: Dict[str, Type[BasePage]] = {}
    _page_instances: Dict[str, BasePage] = {}
    
    @classmethod
    def register_page(cls, page_name: str, page_class: Type[BasePage]):
        """注册页面类"""
        cls._page_registry[page_name] = page_class
        logger.debug(f"注册页面类: {page_name} -> {page_class.__name__}")
    
    @classmethod
    def create_page(cls, page_name: str, driver: WebDriver = None, **kwargs) -> BasePage:
        """创建页面实例"""
        if page_name not in cls._page_registry:
            raise ValueError(f"未注册的页面: {page_name}")
        
        page_class = cls._page_registry[page_name]
        driver = driver or driver_manager.get_driver()
        
        if not driver:
            raise RuntimeError("未找到可用的WebDriver实例")
        
        page_instance = page_class(driver, **kwargs)
        cls._page_instances[page_name] = page_instance
        
        logger.info(f"创建页面实例: {page_name}")
        return page_instance
    
    @classmethod
    def get_page(cls, page_name: str) -> BasePage:
        """获取页面实例"""
        if page_name in cls._page_instances:
            return cls._page_instances[page_name]
        
        # 如果实例不存在，尝试创建
        return cls.create_page(page_name)
    
    @classmethod
    def clear_page_instances(cls):
        """清空页面实例缓存"""
        cls._page_instances.clear()
        logger.info("已清空页面实例缓存")
    
    @classmethod
    def get_registered_pages(cls) -> Dict[str, Type[BasePage]]:
        """获取已注册的页面类"""
        return cls._page_registry.copy()


def page_register(page_name: str):
    """页面注册装饰器"""
    def decorator(page_class: Type[BasePage]):
        PageFactory.register_page(page_name, page_class)
        return page_class
    return decorator


class PageNavigator:
    """页面导航器"""
    
    def __init__(self, driver: WebDriver = None):
        self.driver = driver or driver_manager.get_driver()
        self.current_page: BasePage = None
        self.page_stack: list = []
    
    def navigate_to(self, page_name: str, **kwargs) -> BasePage:
        """导航到指定页面"""
        page = PageFactory.create_page(page_name, self.driver, **kwargs)
        
        # 保存当前页面到栈中
        if self.current_page:
            self.page_stack.append(self.current_page)
        
        self.current_page = page
        logger.info(f"导航到页面: {page_name}")
        return page
    
    def go_back(self) -> BasePage:
        """返回上一个页面"""
        if self.page_stack:
            self.current_page = self.page_stack.pop()
            logger.info("返回上一个页面")
            return self.current_page
        else:
            logger.warning("没有上一个页面可返回")
            return self.current_page
    
    def get_current_page(self) -> BasePage:
        """获取当前页面"""
        return self.current_page
    
    def clear_navigation_stack(self):
        """清空导航栈"""
        self.page_stack.clear()
        self.current_page = None
        logger.info("已清空导航栈")