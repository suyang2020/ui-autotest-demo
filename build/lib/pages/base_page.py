"""
基础页面类
提供页面对象模型的基础功能
"""
import time
from typing import List, Tuple, Optional, Union
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from ..config import config
from ..core import driver_manager
import logging

logger = logging.getLogger(__name__)


class BasePage:
    """基础页面类"""
    
    def __init__(self, driver: WebDriver = None):
        self.driver = driver or driver_manager.get_driver()
        if not self.driver:
            raise RuntimeError("未找到可用的WebDriver实例")
        
        self.wait = WebDriverWait(self.driver, config.get_test_config().get('default_timeout', 10))
        self.timeout = config.get_test_config().get('default_timeout', 10)
    
    # 元素定位方法
    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """查找单个元素"""
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            logger.debug(f"找到元素: {locator}")
            return element
        except TimeoutException:
            logger.error(f"查找元素超时: {locator}")
            raise NoSuchElementException(f"元素定位超时: {locator}")
    
    def find_elements(self, locator: Tuple[str, str], timeout: int = None) -> List[WebElement]:
        """查找多个元素"""
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            elements = self.driver.find_elements(*locator)
            logger.debug(f"找到 {len(elements)} 个元素: {locator}")
            return elements
        except TimeoutException:
            logger.warning(f"查找元素超时: {locator}")
            return []
    
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """等待元素可见"""
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.debug(f"元素可见: {locator}")
            return element
        except TimeoutException:
            logger.error(f"等待元素可见超时: {locator}")
            raise TimeoutException(f"元素可见超时: {locator}")
    
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """等待元素可点击"""
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            logger.debug(f"元素可点击: {locator}")
            return element
        except TimeoutException:
            logger.error(f"等待元素可点击超时: {locator}")
            raise TimeoutException(f"元素可点击超时: {locator}")
    
    def is_element_present(self, locator: Tuple[str, str], timeout: int = 3) -> bool:
        """检查元素是否存在"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 3) -> bool:
        """检查元素是否可见"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    # 基础操作方法
    def click(self, locator: Tuple[str, str], timeout: int = None):
        """点击元素"""
        element = self.wait_for_element_clickable(locator, timeout)
        element.click()
        logger.info(f"点击元素: {locator}")
    
    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True, timeout: int = None):
        """输入文本"""
        element = self.wait_for_element_visible(locator, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.info(f"输入文本 '{text}' 到元素: {locator}")
    
    def get_text(self, locator: Tuple[str, str], timeout: int = None) -> str:
        \"\"\"获取元素文本\"\"\"
        element = self.wait_for_element_visible(locator, timeout)
        text = element.text
        logger.debug(f"获取元素文本 '{text}': {locator}")
        return text
    
    def get_attribute(self, locator: Tuple[str, str], attribute: str, timeout: int = None) -> str:
        \"\"\"获取元素属性\"\"\"
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        logger.debug(f"获取元素属性 {attribute}='{value}': {locator}")
        return value
    
    def clear_text(self, locator: Tuple[str, str], timeout: int = None):
        \"\"\"清空文本\"\"\"
        element = self.find_element(locator, timeout)
        element.clear()
        logger.info(f"清空元素文本: {locator}")
    
    # 滑动和手势操作
    def swipe_up(self, duration: int = 1000):
        \"\"\"向上滑动\"\"\"
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.8
        end_y = size['height'] * 0.2
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        logger.info("执行向上滑动")
    
    def swipe_down(self, duration: int = 1000):
        \"\"\"向下滑动\"\"\"
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.2
        end_y = size['height'] * 0.8
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        logger.info("执行向下滑动")
    
    def swipe_left(self, duration: int = 1000):
        \"\"\"向左滑动\"\"\"
        size = self.driver.get_window_size()
        start_x = size['width'] * 0.8
        start_y = size['height'] // 2
        end_x = size['width'] * 0.2
        self.driver.swipe(start_x, start_y, end_x, start_y, duration)
        logger.info("执行向左滑动")
    
    def swipe_right(self, duration: int = 1000):
        \"\"\"向右滑动\"\"\"
        size = self.driver.get_window_size()
        start_x = size['width'] * 0.2
        start_y = size['height'] // 2
        end_x = size['width'] * 0.8
        self.driver.swipe(start_x, start_y, end_x, start_y, duration)
        logger.info("执行向右滑动")
    
    def scroll_to_element(self, locator: Tuple[str, str], max_scrolls: int = 10, direction: str = 'up') -> WebElement:
        \"\"\"滚动到指定元素\"\"\"
        for i in range(max_scrolls):
            if self.is_element_visible(locator):
                return self.find_element(locator)
            
            if direction == 'up':
                self.swipe_up()
            elif direction == 'down':
                self.swipe_down()
            elif direction == 'left':
                self.swipe_left()
            elif direction == 'right':
                self.swipe_right()
            
            time.sleep(0.5)
        
        raise NoSuchElementException(f"滚动 {max_scrolls} 次后仍未找到元素: {locator}")
    
    # 等待方法
    def wait_for_page_load(self, timeout: int = None):
        \"\"\"等待页面加载完成\"\"\"
        timeout = timeout or self.timeout
        # 这里可以根据具体应用的加载指示器来实现
        time.sleep(1)  # 简单的等待实现
        logger.info("页面加载完成")
    
    def wait_for_text_present(self, text: str, timeout: int = None) -> bool:
        \"\"\"等待文本出现\"\"\"
        timeout = timeout or self.timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            if text in self.driver.page_source:
                logger.debug(f"文本 '{text}' 已出现")
                return True
            time.sleep(0.5)
        
        logger.warning(f"等待文本 '{text}' 超时")
        return False
    
    def wait_for_text_disappear(self, text: str, timeout: int = None) -> bool:
        \"\"\"等待文本消失\"\"\"
        timeout = timeout or self.timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            if text not in self.driver.page_source:
                logger.debug(f"文本 '{text}' 已消失")
                return True
            time.sleep(0.5)
        
        logger.warning(f"等待文本 '{text}' 消失超时")
        return False
    
    # 应用操作
    def go_back(self):
        \"\"\"返回上一页\"\"\"
        self.driver.back()
        logger.info("执行返回操作")
    
    def hide_keyboard(self):
        \"\"\"隐藏键盘\"\"\"
        try:
            self.driver.hide_keyboard()
            logger.info("隐藏键盘")
        except Exception:
            logger.debug("无键盘需要隐藏")
    
    def get_current_activity(self) -> str:
        \"\"\"获取当前Activity（Android）\"\"\"
        try:
            activity = self.driver.current_activity
            logger.debug(f"当前Activity: {activity}")
            return activity
        except Exception:
            return ""
    
    def take_screenshot(self, filename: str = None) -> str:
        \"\"\"截图\"\"\"
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_dir = config.get_test_config().get('screenshot_dir', './screenshots')
        import os
        os.makedirs(screenshot_dir, exist_ok=True)
        
        filepath = os.path.join(screenshot_dir, filename)
        self.driver.save_screenshot(filepath)
        logger.info(f"截图保存到: {filepath}")
        return filepath


class ElementLocators:
    \"\"\"元素定位器集合\"\"\"
    
    # Android定位器
    @staticmethod
    def android_id(resource_id: str) -> Tuple[str, str]:
        \"\"\"Android ID定位\"\"\"
        return (AppiumBy.ID, resource_id)
    
    @staticmethod
    def android_xpath(xpath: str) -> Tuple[str, str]:
        \"\"\"Android XPath定位\"\"\"
        return (AppiumBy.XPATH, xpath)
    
    @staticmethod
    def android_class(class_name: str) -> Tuple[str, str]:
        \"\"\"Android 类名定位\"\"\"
        return (AppiumBy.CLASS_NAME, class_name)
    
    @staticmethod
    def android_text(text: str) -> Tuple[str, str]:
        \"\"\"Android 文本定位\"\"\"
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
    
    @staticmethod
    def android_contains_text(text: str) -> Tuple[str, str]:
        \"\"\"Android 包含文本定位\"\"\"
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
    
    @staticmethod
    def android_description(description: str) -> Tuple[str, str]:
        \"\"\"Android 内容描述定位\"\"\"
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("{description}")')
    
    # iOS定位器
    @staticmethod
    def ios_predicate(predicate: str) -> Tuple[str, str]:
        \"\"\"iOS Predicate定位\"\"\"
        return (AppiumBy.IOS_PREDICATE, predicate)
    
    @staticmethod
    def ios_class_chain(class_chain: str) -> Tuple[str, str]:
        \"\"\"iOS Class Chain定位\"\"\"
        return (AppiumBy.IOS_CLASS_CHAIN, class_chain)
    
    @staticmethod
    def accessibility_id(accessibility_id: str) -> Tuple[str, str]:
        \"\"\"Accessibility ID定位（跨平台）\"\"\"
        return (AppiumBy.ACCESSIBILITY_ID, accessibility_id)