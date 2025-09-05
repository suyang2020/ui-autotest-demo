"""
登录页面对象
演示POM模式的具体实现
"""
from typing import Tuple
from appium.webdriver.common.appiumby import AppiumBy
from ..base_page import BasePage, ElementLocators
from ..page_factory import page_register
from ...utils import get_logger, log_step

logger = get_logger(__name__)


@page_register("login_page")
class LoginPage(BasePage):
    """登录页面"""
    
    # 页面元素定位器
    USERNAME_INPUT = ElementLocators.android_id("com.example.app:id/username")
    PASSWORD_INPUT = ElementLocators.android_id("com.example.app:id/password")
    LOGIN_BUTTON = ElementLocators.android_id("com.example.app:id/login_btn")
    REGISTER_LINK = ElementLocators.android_id("com.example.app:id/register_link")
    FORGOT_PASSWORD_LINK = ElementLocators.android_id("com.example.app:id/forgot_password")
    ERROR_MESSAGE = ElementLocators.android_id("com.example.app:id/error_message")
    
    # 替代定位器（用于不同版本的应用）
    USERNAME_INPUT_ALT = ElementLocators.android_xpath("//android.widget.EditText[@hint='用户名']")
    PASSWORD_INPUT_ALT = ElementLocators.android_xpath("//android.widget.EditText[@hint='密码']")
    LOGIN_BUTTON_ALT = ElementLocators.android_text("登录")
    
    def __init__(self, driver=None):
        super().__init__(driver)
        self.page_name = "登录页面"
    
    @log_step("等待登录页面加载")
    def wait_for_page_load(self, timeout: int = 15):
        """等待登录页面加载完成"""
        try:
            self.wait_for_element_visible(self.USERNAME_INPUT, timeout)
            logger.info("登录页面加载完成")
        except Exception:
            # 尝试替代定位器
            self.wait_for_element_visible(self.USERNAME_INPUT_ALT, timeout)
            logger.info("登录页面加载完成（使用替代定位器）")
    
    def is_login_page(self) -> bool:
        """检查是否为登录页面"""
        return (self.is_element_present(self.USERNAME_INPUT) or 
                self.is_element_present(self.USERNAME_INPUT_ALT))
    
    @log_step("输入用户名")
    def enter_username(self, username: str):
        """输入用户名"""
        try:
            self.send_keys(self.USERNAME_INPUT, username)
        except Exception:
            self.send_keys(self.USERNAME_INPUT_ALT, username)
        logger.info(f"输入用户名: {username}")
    
    @log_step("输入密码")
    def enter_password(self, password: str):
        """输入密码"""
        try:
            self.send_keys(self.PASSWORD_INPUT, password, clear_first=True)
        except Exception:
            self.send_keys(self.PASSWORD_INPUT_ALT, password, clear_first=True)
        logger.info("输入密码: ****")
    
    @log_step("点击登录按钮")
    def click_login_button(self):
        """点击登录按钮"""
        try:
            self.click(self.LOGIN_BUTTON)
        except Exception:
            self.click(self.LOGIN_BUTTON_ALT)
        logger.info("点击登录按钮")
    
    @log_step("执行登录操作")
    def login(self, username: str, password: str):
        """执行登录操作"""
        self.wait_for_page_load()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        logger.info(f"执行登录操作: {username}")
    
    def click_register_link(self):
        """点击注册链接"""
        self.click(self.REGISTER_LINK)
        logger.info("点击注册链接")
    
    def click_forgot_password_link(self):
        """点击忘记密码链接"""
        self.click(self.FORGOT_PASSWORD_LINK)
        logger.info("点击忘记密码链接")
    
    def get_error_message(self) -> str:
        """获取错误信息"""
        if self.is_element_visible(self.ERROR_MESSAGE, timeout=3):
            error_text = self.get_text(self.ERROR_MESSAGE)
            logger.info(f"获取到错误信息: {error_text}")
            return error_text
        return ""
    
    def is_login_successful(self) -> bool:
        """检查登录是否成功（通过检查是否离开登录页面）"""
        import time
        time.sleep(2)  # 等待页面跳转
        return not self.is_login_page()
    
    def clear_username(self):
        """清空用户名"""
        try:
            self.clear_text(self.USERNAME_INPUT)
        except Exception:
            self.clear_text(self.USERNAME_INPUT_ALT)
        logger.info("清空用户名")
    
    def clear_password(self):
        """清空密码"""
        try:
            self.clear_text(self.PASSWORD_INPUT)
        except Exception:
            self.clear_text(self.PASSWORD_INPUT_ALT)
        logger.info("清空密码")
    
    def clear_form(self):
        """清空表单"""
        self.clear_username()
        self.clear_password()
        logger.info("清空登录表单")


class QuickLogin:
    """快速登录工具类"""
    
    def __init__(self, login_page: LoginPage):
        self.login_page = login_page
    
    def admin_login(self):
        """管理员登录"""
        self.login_page.login("admin", "admin123")
    
    def user_login(self):
        """普通用户登录"""
        self.login_page.login("testuser", "test123")
    
    def invalid_login(self):
        """无效登录（用于测试错误场景）"""
        self.login_page.login("invalid_user", "invalid_password")