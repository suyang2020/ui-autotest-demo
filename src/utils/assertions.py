"""
断言工具模块
提供丰富的断言方法用于测试验证
"""
import time
from typing import Any, List, Union, Callable
from appium.webdriver.webdriver import WebDriver
from .logger import get_logger
from ..core import driver_manager

logger = get_logger(__name__)


class Assert:
    """断言工具类"""
    
    @staticmethod
    def equal(actual: Any, expected: Any, message: str = None):
        """断言相等"""
        message = message or f"期望值: {expected}, 实际值: {actual}"
        try:
            assert actual == expected, message
            logger.info(f"断言通过 - 相等: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 相等: {e}")
            raise
    
    @staticmethod
    def not_equal(actual: Any, expected: Any, message: str = None):
        """断言不相等"""
        message = message or f"值不应该等于: {expected}, 实际值: {actual}"
        try:
            assert actual != expected, message
            logger.info(f"断言通过 - 不相等: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 不相等: {e}")
            raise
    
    @staticmethod
    def true(condition: bool, message: str = None):
        """断言为真"""
        message = message or f"条件应该为True"
        try:
            assert condition is True, message
            logger.info(f"断言通过 - 为真: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 为真: {e}")
            raise
    
    @staticmethod
    def false(condition: bool, message: str = None):
        """断言为假"""
        message = message or f"条件应该为False"
        try:
            assert condition is False, message
            logger.info(f"断言通过 - 为假: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 为假: {e}")
            raise
    
    @staticmethod
    def contains(container: Union[str, List], item: Any, message: str = None):
        """断言包含"""
        message = message or f"'{container}' 应该包含 '{item}'"
        try:
            assert item in container, message
            logger.info(f"断言通过 - 包含: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 包含: {e}")
            raise
    
    @staticmethod
    def not_contains(container: Union[str, List], item: Any, message: str = None):
        """断言不包含"""
        message = message or f"'{container}' 不应该包含 '{item}'"
        try:
            assert item not in container, message
            logger.info(f"断言通过 - 不包含: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 不包含: {e}")
            raise
    
    @staticmethod
    def greater_than(actual: Union[int, float], expected: Union[int, float], message: str = None):
        """断言大于"""
        message = message or f"{actual} 应该大于 {expected}"
        try:
            assert actual > expected, message
            logger.info(f"断言通过 - 大于: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 大于: {e}")
            raise
    
    @staticmethod
    def less_than(actual: Union[int, float], expected: Union[int, float], message: str = None):
        """断言小于"""
        message = message or f"{actual} 应该小于 {expected}"
        try:
            assert actual < expected, message
            logger.info(f"断言通过 - 小于: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 小于: {e}")
            raise
    
    @staticmethod
    def starts_with(text: str, prefix: str, message: str = None):
        """断言以指定文本开头"""
        message = message or f"'{text}' 应该以 '{prefix}' 开头"
        try:
            assert text.startswith(prefix), message
            logger.info(f"断言通过 - 开头: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 开头: {e}")
            raise
    
    @staticmethod
    def ends_with(text: str, suffix: str, message: str = None):
        """断言以指定文本结尾"""
        message = message or f"'{text}' 应该以 '{suffix}' 结尾"
        try:
            assert text.endswith(suffix), message
            logger.info(f"断言通过 - 结尾: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 结尾: {e}")
            raise


class ElementAssert:
    """元素断言类"""
    
    def __init__(self, driver: WebDriver = None):
        self.driver = driver or driver_manager.get_driver()
    
    def element_present(self, locator: tuple, timeout: int = 10, message: str = None):
        """断言元素存在"""
        from ..pages.base_page import BasePage
        page = BasePage(self.driver)
        
        message = message or f"元素应该存在: {locator}"
        try:
            is_present = page.is_element_present(locator, timeout)
            assert is_present, message
            logger.info(f"断言通过 - 元素存在: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 元素存在: {e}")
            raise
    
    def element_not_present(self, locator: tuple, timeout: int = 3, message: str = None):
        """断言元素不存在"""
        from ..pages.base_page import BasePage
        page = BasePage(self.driver)
        
        message = message or f"元素不应该存在: {locator}"
        try:
            is_present = page.is_element_present(locator, timeout)
            assert not is_present, message
            logger.info(f"断言通过 - 元素不存在: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 元素不存在: {e}")
            raise
    
    def element_visible(self, locator: tuple, timeout: int = 10, message: str = None):
        """断言元素可见"""
        from ..pages.base_page import BasePage
        page = BasePage(self.driver)
        
        message = message or f"元素应该可见: {locator}"
        try:
            is_visible = page.is_element_visible(locator, timeout)
            assert is_visible, message
            logger.info(f"断言通过 - 元素可见: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 元素可见: {e}")
            raise
    
    def element_text_equal(self, locator: tuple, expected_text: str, timeout: int = 10, message: str = None):
        """断言元素文本相等"""
        from ..pages.base_page import BasePage
        page = BasePage(self.driver)
        
        actual_text = page.get_text(locator, timeout)
        message = message or f"元素文本应该是 '{expected_text}', 实际是 '{actual_text}'"
        
        try:
            assert actual_text == expected_text, message
            logger.info(f"断言通过 - 元素文本相等: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 元素文本相等: {e}")
            raise
    
    def element_text_contains(self, locator: tuple, expected_text: str, timeout: int = 10, message: str = None):
        """断言元素文本包含"""
        from ..pages.base_page import BasePage
        page = BasePage(self.driver)
        
        actual_text = page.get_text(locator, timeout)
        message = message or f"元素文本 '{actual_text}' 应该包含 '{expected_text}'"
        
        try:
            assert expected_text in actual_text, message
            logger.info(f"断言通过 - 元素文本包含: {message}")
        except AssertionError as e:
            logger.error(f"断言失败 - 元素文本包含: {e}")
            raise


class WaitAssert:
    """等待断言类"""
    
    def __init__(self, driver: WebDriver = None):
        self.driver = driver or driver_manager.get_driver()
    
    def wait_until_true(self, condition: Callable[[], bool], timeout: int = 30, 
                       interval: float = 0.5, message: str = None):
        """等待条件为真"""
        message = message or "等待条件为真"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition():
                    logger.info(f"等待断言通过: {message}")
                    return True
            except Exception:
                pass
            time.sleep(interval)
        
        logger.error(f"等待断言超时: {message}")
        raise AssertionError(f"等待超时: {message}")
    
    def wait_until_false(self, condition: Callable[[], bool], timeout: int = 30, 
                        interval: float = 0.5, message: str = None):
        """等待条件为假"""
        message = message or "等待条件为假"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if not condition():
                    logger.info(f"等待断言通过: {message}")
                    return True
            except Exception:
                pass
            time.sleep(interval)
        
        logger.error(f"等待断言超时: {message}")
        raise AssertionError(f"等待超时: {message}")


# 便捷函数
def assert_equal(actual: Any, expected: Any, message: str = None):
    """断言相等的便捷函数"""
    Assert.equal(actual, expected, message)


def assert_true(condition: bool, message: str = None):
    """断言为真的便捷函数"""
    Assert.true(condition, message)


def assert_element_present(locator: tuple, timeout: int = 10, message: str = None, driver: WebDriver = None):
    """断言元素存在的便捷函数"""
    ElementAssert(driver).element_present(locator, timeout, message)