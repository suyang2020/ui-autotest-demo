"""
登录功能测试用例
演示基础功能测试和数据驱动测试
"""
import pytest
import allure
from ..base_test import AndroidTest
from ...pages.page_factory import PageFactory
from ...pages.app import LoginPage, HomePage, QuickLogin
from ...utils import assert_true, assert_equal, get_test_data, generate_user_data
from ...utils import log_step, take_step_screenshot

@allure.epic("用户管理")
@allure.feature("登录功能")
class TestLogin(AndroidTest):
    """登录功能测试类"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
    
    @allure.story("正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_valid_login(self):
        """测试有效用户登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
            take_step_screenshot("登录页面加载完成")
        
        with allure.step("输入有效的用户名和密码"):
            self.login_page.enter_username("testuser")
            self.login_page.enter_password("test123")
            take_step_screenshot("输入登录信息")
        
        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()
        
        with allure.step("验证登录成功"):
            # 等待页面跳转
            self.home_page.wait_for_page_load()
            assert_true(self.home_page.is_home_page(), "应该跳转到主页面")
            take_step_screenshot("登录成功")
    
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_invalid_login(self):
        """测试无效用户登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("输入无效的用户名和密码"):
            self.login_page.enter_username("invalid_user")
            self.login_page.enter_password("invalid_password")
        
        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()
        
        with allure.step("验证登录失败"):
            # 检查是否还在登录页面
            assert_true(self.login_page.is_login_page(), "应该还在登录页面")
            
            # 检查错误信息
            error_message = self.login_page.get_error_message()
            assert_true(len(error_message) > 0, "应该显示错误信息")
            take_step_screenshot("登录失败显示错误信息")
    
    @allure.story("空用户名登录")
    @allure.severity(allure.severity_level.MINOR)
    def test_empty_username_login(self):
        """测试空用户名登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("输入空用户名和有效密码"):
            self.login_page.enter_username("")
            self.login_page.enter_password("test123")
        
        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()
        
        with allure.step("验证登录失败"):
            assert_true(self.login_page.is_login_page(), "应该还在登录页面")
            error_message = self.login_page.get_error_message()
            assert_true("用户名" in error_message or "username" in error_message.lower(), 
                       "应该提示用户名相关错误")
    
    @allure.story("空密码登录")
    @allure.severity(allure.severity_level.MINOR)
    def test_empty_password_login(self):
        """测试空密码登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("输入有效用户名和空密码"):
            self.login_page.enter_username("testuser")
            self.login_page.enter_password("")
        
        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()
        
        with allure.step("验证登录失败"):
            assert_true(self.login_page.is_login_page(), "应该还在登录页面")
            error_message = self.login_page.get_error_message()
            assert_true("密码" in error_message or "password" in error_message.lower(), 
                       "应该提示密码相关错误")
    
    @allure.story("快速登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_quick_login_admin(self):
        """测试管理员快速登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("使用快速登录工具"):
            quick_login = QuickLogin(self.login_page)
            quick_login.admin_login()
        
        with allure.step("验证登录成功"):
            self.home_page.wait_for_page_load()
            assert_true(self.home_page.is_home_page(), "管理员应该能成功登录")
    
    @allure.story("清空表单")
    @allure.severity(allure.severity_level.TRIVIAL)
    def test_clear_login_form(self):
        """测试清空登录表单"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("输入用户名和密码"):
            self.login_page.enter_username("testuser")
            self.login_page.enter_password("testpassword")
        
        with allure.step("清空表单"):
            self.login_page.clear_form()
        
        with allure.step("验证表单已清空"):
            # 这里可以添加验证逻辑，比如检查输入框是否为空
            take_step_screenshot("表单已清空")


# 数据驱动测试
@allure.epic("用户管理")
@allure.feature("登录功能")
@allure.story("数据驱动登录测试")
class TestLoginDataDriven(AndroidTest):
    """数据驱动登录测试"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
    
    @pytest.mark.parametrize("username,password,expected", [
        ("valid_user", "valid_password", "success"),
        ("invalid_user", "valid_password", "fail"),
        ("valid_user", "invalid_password", "fail"),
        ("", "valid_password", "fail"),
        ("valid_user", "", "fail"),
        ("admin", "admin123", "success"),
        ("guest", "guest123", "success"),
    ])
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_with_different_credentials(self, username, password, expected):
        """使用不同凭据测试登录"""
        allure.dynamic.title(f"登录测试: {username} / {'*' * len(password)}")
        
        with allure.step(f"测试用户 {username} 登录"):
            self.login_page.wait_for_page_load()
            self.login_page.login(username, password)
        
        if expected == "success":
            with allure.step("验证登录成功"):
                self.home_page.wait_for_page_load()
                assert_true(self.home_page.is_home_page(), f"用户 {username} 应该能成功登录")
        else:
            with allure.step("验证登录失败"):
                assert_true(self.login_page.is_login_page(), f"用户 {username} 登录应该失败")
                error_message = self.login_page.get_error_message()
                assert_true(len(error_message) > 0, "应该显示错误信息")
    
    @pytest.mark.parametrize("user_data", [
        generate_user_data("normal"),
        generate_user_data("admin"),
        generate_user_data("vip"),
    ])
    @allure.severity(allure.severity_level.MINOR)
    def test_login_with_generated_users(self, user_data):
        """使用生成的用户数据测试登录"""
        allure.dynamic.title(f"生成用户登录测试: {user_data['username']}")
        
        with allure.step(f"使用生成的用户数据登录: {user_data['username']}"):
            self.login_page.wait_for_page_load()
            self.login_page.login(user_data['username'], user_data['password'])
        
        with allure.step("验证登录结果"):
            # 由于是随机生成的用户，预期应该登录失败
            assert_true(self.login_page.is_login_page(), "随机生成的用户应该登录失败")


@allure.epic("用户管理")
@allure.feature("登录功能")
@allure.story("登录性能测试")
class TestLoginPerformance(AndroidTest):
    """登录性能测试"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
    
    @allure.severity(allure.severity_level.MINOR)
    def test_login_response_time(self):
        """测试登录响应时间"""
        import time
        
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("记录登录开始时间"):
            start_time = time.time()
            self.login_page.login("testuser", "test123")
        
        with allure.step("等待登录完成并记录结束时间"):
            self.home_page.wait_for_page_load()
            end_time = time.time()
            
            response_time = end_time - start_time
            allure.attach(f"登录响应时间: {response_time:.2f} 秒", name="响应时间", 
                         attachment_type=allure.attachment_type.TEXT)
            
            # 断言响应时间应该在合理范围内（比如5秒内）
            assert_true(response_time < 5.0, f"登录响应时间应该小于5秒，实际: {response_time:.2f}秒")
    
    @allure.severity(allure.severity_level.TRIVIAL)
    def test_multiple_login_attempts(self):
        """测试多次登录尝试"""
        attempt_count = 3
        
        for i in range(attempt_count):
            with allure.step(f"第 {i+1} 次登录尝试"):
                if i > 0:
                    # 如果不是第一次，需要先退出登录
                    if self.home_page.is_home_page():
                        self.home_page.click_logout()
                        self.login_page.wait_for_page_load()
                
                self.login_page.login("testuser", "test123")
                self.home_page.wait_for_page_load()
                assert_true(self.home_page.is_home_page(), f"第 {i+1} 次登录应该成功")