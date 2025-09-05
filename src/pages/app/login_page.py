"""
登录页面对象
基于实际应用XML源码分析的元素定位器
"""
from typing import Tuple
from appium.webdriver.common.appiumby import AppiumBy
from ..base_page import BasePage, ElementLocators
from ..page_factory import page_register
from ...utils import get_logger, log_step
import time


logger = get_logger(__name__)


@page_register("login_page")
class LoginPage(BasePage):
    """登录页面 - 基于WebView的登录界面"""
    
    # 页面元素定位器 - 基于实际XML源码分析
    # 主要容器
    WEBVIEW_CONTAINER = ElementLocators.android_class("android.webkit.WebView")
    LOGIN_WEBVIEW = ElementLocators.android_text("pages/login[1]")
    
    # Logo图标
    HOME_LOGO = ElementLocators.android_text("home")
    
    # 手机号输入相关
    PHONE_INPUT_PLACEHOLDER = ElementLocators.android_text("请输入手机号")
    PHONE_INPUT = ElementLocators.android_xpath("//android.widget.EditText[contains(@bounds,'[139,330][649,361')]")
    PHONE_INPUT_ALT = ElementLocators.android_xpath("//android.view.View[@text='请输入手机号']/../android.widget.EditText")
    
    # 验证码输入相关
    VERIFICATION_CODE_PLACEHOLDER = ElementLocators.android_text("请输入验证码")
    VERIFICATION_CODE_INPUT = ElementLocators.android_xpath("//android.widget.EditText[contains(@bounds,'[139,427][414,459')]")
    VERIFICATION_CODE_INPUT_ALT = ElementLocators.android_xpath("//android.view.View[@text='请输入验证码']/../android.widget.EditText")
    
    # 获取验证码按钮
    GET_VERIFICATION_CODE_BUTTON = ElementLocators.android_text("获取验证码")
    GET_VERIFICATION_CODE_BUTTON_ALT = ElementLocators.android_xpath("//android.view.View[@text='获取验证码' and @clickable='true']")
    
    # 登录按钮
    LOGIN_BUTTON = ElementLocators.android_text("登录")
    LOGIN_BUTTON_ALT = ElementLocators.android_xpath("//android.view.View[@text='登录' and @clickable='true']")
    
    # 微信一键登录
    WECHAT_LOGIN_CONTAINER = ElementLocators.android_text("微信一键登录")
    WECHAT_LOGIN_BUTTON = ElementLocators.android_xpath("//android.view.View[@text='微信一键登录']/../..")
    
    # 协议相关
    AGREEMENT_CHECKBOX = ElementLocators.android_xpath("//android.view.View[@clickable='true' and contains(@bounds,'[106,730][135,759]')]")
    AGREEMENT_TEXT = ElementLocators.android_text("登录即代表同意")
    USER_AGREEMENT_LINK = ElementLocators.android_text("《用户注册协议》")
    PRIVACY_AGREEMENT_LINK = ElementLocators.android_text("《隐私协议》")
    
    # 底部导航元素（用于判断是否已登录）
    TAB_MESSAGE = ElementLocators.android_text("消息")
    TAB_CONTACTS = ElementLocators.android_text("通讯录")
    TAB_DISCOVER = ElementLocators.android_text("发现精彩")
    TAB_PROFILE = ElementLocators.android_text("我的")
    
    def __init__(self, driver=None):
        super().__init__(driver)
        self.page_name = "登录页面"
    
    @log_step("等待登录页面加载")
    def wait_for_page_load(self, timeout: int = 15):
        """等待登录页面加载完成"""
        try:
            # 等待WebView容器出现
            self.wait_for_element_visible(self.WEBVIEW_CONTAINER, timeout)
            # 等待登录WebView内容加载
            self.wait_for_element_visible(self.HOME_LOGO, timeout)
            logger.info("登录页面加载完成")
        except Exception as e:
            logger.error(f"等待登录页面加载失败: {e}")
            # 尝试等待手机号输入框
            self.wait_for_element_visible(self.PHONE_INPUT_PLACEHOLDER, timeout)
            logger.info("登录页面加载完成（通过输入框确认）")
    
    def is_login_page(self) -> bool:
        """检查是否为登录页面"""
        return (self.is_element_present(self.PHONE_INPUT_PLACEHOLDER) or 
                self.is_element_present(self.LOGIN_BUTTON) or
                self.is_element_present(self.HOME_LOGO))
    
    @log_step("输入手机号")
    def enter_phone_number(self, phone_number: str):
        """输入手机号"""
        try:
            # 点击手机号输入区域激活输入框
            if self.is_element_visible(self.PHONE_INPUT_PLACEHOLDER, timeout=3):
                self.click(self.PHONE_INPUT_PLACEHOLDER)
            
            # 输入手机号
            if self.is_element_visible(self.PHONE_INPUT, timeout=3):
                self.send_keys(self.PHONE_INPUT, phone_number, clear_first=True)
            else:
                self.send_keys(self.PHONE_INPUT_ALT, phone_number, clear_first=True)
            
            logger.info(f"输入手机号: {phone_number}")
        except Exception as e:
            logger.error(f"输入手机号失败: {e}")
            raise
    
    @log_step("点击获取验证码")
    def click_get_verification_code(self):
        """点击获取验证码按钮"""
        try:
            if self.is_element_visible(self.GET_VERIFICATION_CODE_BUTTON, timeout=3):
                self.click(self.GET_VERIFICATION_CODE_BUTTON)
            else:
                self.click(self.GET_VERIFICATION_CODE_BUTTON_ALT)
            logger.info("点击获取验证码按钮")
        except Exception as e:
            logger.error(f"点击获取验证码失败: {e}")
            raise
    
    @log_step("输入验证码")
    def enter_verification_code(self, code: str):
        """输入验证码"""
        try:
            # 点击验证码输入区域激活输入框
            if self.is_element_visible(self.VERIFICATION_CODE_PLACEHOLDER, timeout=3):
                self.click(self.VERIFICATION_CODE_PLACEHOLDER)
            
            # 输入验证码
            if self.is_element_visible(self.VERIFICATION_CODE_INPUT, timeout=3):
                self.send_keys(self.VERIFICATION_CODE_INPUT, code, clear_first=True)
            else:
                self.send_keys(self.VERIFICATION_CODE_INPUT_ALT, code, clear_first=True)
            
            logger.info(f"输入验证码: ****")
        except Exception as e:
            logger.error(f"输入验证码失败: {e}")
            raise
    
    @log_step("点击登录按钮")
    def click_login_button(self):
        """点击登录按钮"""
        try:
            if self.is_element_visible(self.LOGIN_BUTTON, timeout=3):
                self.click(self.LOGIN_BUTTON)
            else:
                self.click(self.LOGIN_BUTTON_ALT)
            logger.info("点击登录按钮")
        except Exception as e:
            logger.error(f"点击登录失败: {e}")
            raise
    
    @log_step("点击微信一键登录")
    def click_wechat_login(self):
        """点击微信一键登录"""
        try:
            if self.is_element_visible(self.WECHAT_LOGIN_CONTAINER, timeout=3):
                self.click(self.WECHAT_LOGIN_BUTTON)
                logger.info("点击微信一键登录")
            else:
                logger.warning("微信一键登录按钮不可见")
        except Exception as e:
            logger.error(f"点击微信一键登录失败: {e}")
            raise
    
    @log_step("同意协议")
    def agree_to_terms(self):
        """勾选同意协议复选框"""
        try:
            if self.is_element_visible(self.AGREEMENT_CHECKBOX, timeout=3):
                self.click(self.AGREEMENT_CHECKBOX)
                logger.info("勾选同意协议")
            else:
                logger.info("协议复选框可能已经勾选或不存在")
        except Exception as e:
            logger.error(f"勾选协议失败: {e}")
            # 不抛出异常，因为有些版本可能默认已勾选
    
    @log_step("执行验证码登录")
    def login_with_verification_code(self, phone_number: str, verification_code: str, agree_terms: bool = True):
        """执行完整的验证码登录流程"""
        self.wait_for_page_load()
        
        if agree_terms:
            self.agree_to_terms()
        
        self.enter_phone_number(phone_number)
        self.click_get_verification_code()
        
        # 等待验证码发送成功
        time.sleep(2)
        
        self.enter_verification_code(verification_code)
        self.click_login_button()
        
        logger.info(f"执行验证码登录: {phone_number}")
    
    def is_login_successful(self) -> bool:
        """检查登录是否成功（通过检查底部导航栏）"""
        time.sleep(3)  # 等待页面跳转
        
        # 检查是否出现底部导航栏
        return (self.is_element_visible(self.TAB_MESSAGE, timeout=5) or 
                self.is_element_visible(self.TAB_CONTACTS, timeout=3))
    
    def get_current_page_info(self) -> dict:
        """获取当前页面信息（用于调试）"""
        info = {
            "is_login_page": self.is_login_page(),
            "webview_present": self.is_element_present(self.WEBVIEW_CONTAINER),
            "logo_present": self.is_element_present(self.HOME_LOGO),
            "phone_input_present": self.is_element_present(self.PHONE_INPUT_PLACEHOLDER),
            "login_button_present": self.is_element_present(self.LOGIN_BUTTON),
            "wechat_login_present": self.is_element_present(self.WECHAT_LOGIN_CONTAINER),
            "bottom_nav_present": self.is_element_present(self.TAB_MESSAGE)
        }
        logger.info(f"当前页面信息: {info}")
        return info
    
    def clear_phone_input(self):
        """清空手机号输入框"""
        try:
            if self.is_element_visible(self.PHONE_INPUT, timeout=3):
                self.clear_text(self.PHONE_INPUT)
            else:
                self.clear_text(self.PHONE_INPUT_ALT)
            logger.info("清空手机号输入框")
        except Exception as e:
            logger.error(f"清空手机号失败: {e}")
    
    def clear_verification_code_input(self):
        """清空验证码输入框"""
        try:
            if self.is_element_visible(self.VERIFICATION_CODE_INPUT, timeout=3):
                self.clear_text(self.VERIFICATION_CODE_INPUT)
            else:
                self.clear_text(self.VERIFICATION_CODE_INPUT_ALT)
            logger.info("清空验证码输入框")
        except Exception as e:
            logger.error(f"清空验证码失败: {e}")
    
    def clear_form(self):
        """清空登录表单"""
        self.clear_phone_input()
        self.clear_verification_code_input()
        logger.info("清空登录表单")


class QuickWhaleLogin:
    """微鲸灵快速登录工具类"""
    
    def __init__(self, login_page: LoginPage):
        self.login_page = login_page
    
    def test_login(self, phone: str = "13800138000", code: str = "123456"):
        """测试登录（使用模拟数据）"""
        self.login_page.login_with_verification_code(phone, code)
    
    def demo_login_flow(self):
        """演示登录流程（不实际输入数据）"""
        page = self.login_page
        page.wait_for_page_load()
        
        # 显示页面信息
        page.get_current_page_info()
        
        # 演示操作流程（不输入真实数据）
        logger.info("演示登录流程开始...")
        
        # 可以点击输入框查看反应
        if page.is_element_visible(page.PHONE_INPUT_PLACEHOLDER, timeout=3):
            logger.info("手机号输入框可见")
        
        if page.is_element_visible(page.GET_VERIFICATION_CODE_BUTTON, timeout=3):
            logger.info("获取验证码按钮可见")
        
        if page.is_element_visible(page.LOGIN_BUTTON, timeout=3):
            logger.info("登录按钮可见")
        
        logger.info("演示登录流程完成")