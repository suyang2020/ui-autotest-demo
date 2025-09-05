"""
微信鲸登录功能测试用例
基于实际XML源码分析的测试用例
"""
import time
import pytest
import allure
from src.tests.base_test import AndroidTest
from src.pages.page_factory import PageFactory
from src.utils import assert_true, take_step_screenshot, get_logger

logger = get_logger(__name__)

@allure.epic("用户管理")
@allure.feature("登录功能")
class TestLogin(AndroidTest):
    """登录功能测试类"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
    

    @allure.story("输入错误手机号，点获取验证码，登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_error_phone_login(self):
        """测试无效用户登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
        
        with allure.step("输入错误手机号"):
            self.login_page.enter_phone_number("1321000100")

        with allure.step("点击获取验证码"):
            # 使用新的方法来获取Toast提示
            self.login_page.click_get_verification_code()
            take_step_screenshot("点击获取验证码后")
        
        with allure.step("点击登录按钮"):
            # 使用新的方法来获取Toast提示  
            self.login_page.click_login_button()
            take_step_screenshot("点击登录按钮后")
            
        with allure.step("验证登录失败"):
            # 检查是否还在登录页面
            assert_true(self.login_page.is_login_page(), "还在登录页面")


    @allure.story("错误验证码登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_error_code_login_with_toast(self):
        """测试错误验证码登录并验证Toast提示"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
            take_step_screenshot("登录页面加载完成")

        with allure.step("输入正确手机号，点击获取验证码"):
            # 直接点击获取验证码，不输入任何手机号
            self.login_page.enter_phone_number("13210001000")
            self.login_page.click_get_verification_code()

        with allure.step("输入错误验证码"):
            self.login_page.agree_to_terms()

        with allure.step("输入错误验证码"):
            time.sleep(1)
            # 输入错误验证码
            self.login_page.enter_verification_code("141414")

        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()

        with allure.step("验证登录失败"):
            # 等待页面跳转
            assert_true(self.login_page.is_login_page(), "还在登录页面")
            take_step_screenshot("输入错误验证码，登录失败")
            time.sleep(60)

    @allure.story("不勾选同意按钮登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_no_agree_login(self):
        """测试有效用户登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
            take_step_screenshot("登录页面加载完成")

        with allure.step("输入有效的用户名,获取验证码，输入验证码，勾选同意"):
            self.login_page.enter_phone_number("13210001000")

            self.login_page.click_get_verification_code()
            time.sleep(1)
            self.login_page.enter_verification_code("141414")

        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()
            take_step_screenshot("登录失败提示勾选同意协议")

        with allure.step("验证登录失败"):
            # 等待页面跳转
            assert_true(self.login_page.is_login_page(), "还在登录页面")
            take_step_screenshot("输入错误验证码，登录失败")
            # time.sleep(60)


    @allure.story("正常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_valid_login(self):
        """测试有效用户登录"""
        with allure.step("等待登录页面加载"):
            self.login_page.wait_for_page_load()
            take_step_screenshot("登录页面加载完成")

        with allure.step("输入有效的用户名,获取验证码，输入验证码，勾选同意"):
            self.login_page.enter_phone_number("13210101010")

            self.login_page.click_get_verification_code()
            time.sleep(1)
            self.login_page.agree_to_terms()
            self.login_page.enter_verification_code("314141")
            take_step_screenshot("输入登录信息")

        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()

        with allure.step("验证登录成功"):
            # 等待页面跳转
            assert_true(self.login_page.is_login_successful(), "应该跳转到主页面")
            take_step_screenshot("登录成功")



#
# # 数据驱动测试
# @allure.epic("用户管理")
# @allure.feature("登录功能")
# @allure.story("数据驱动登录测试")
# class TestLoginDataDriven(AndroidTest):
#     """数据驱动登录测试"""
#
#     def setup_method(self, method):
#         """测试方法设置"""
#         super().setup_method(method)
#         self.login_page = PageFactory.create_page("login_page", self.driver)
#         self.home_page = PageFactory.create_page("home_page", self.driver)
#
#     @pytest.mark.parametrize("username,password,expected", [
#         ("valid_user", "valid_password", "success"),
#         ("invalid_user", "valid_password", "fail"),
#         ("valid_user", "invalid_password", "fail"),
#         ("", "valid_password", "fail"),
#         ("valid_user", "", "fail"),
#         ("admin", "admin123", "success"),
#         ("guest", "guest123", "success"),
#     ])
#     @allure.severity(allure.severity_level.NORMAL)
#     def test_login_with_different_credentials(self, username, password, expected):
#         """使用不同凭据测试登录"""
#         allure.dynamic.title(f"登录测试: {username} / {'*' * len(password)}")
#
#         with allure.step(f"测试用户 {username} 登录"):
#             self.login_page.wait_for_page_load()
#             self.login_page.login(username, password)
#
#         if expected == "success":
#             with allure.step("验证登录成功"):
#                 self.home_page.wait_for_page_load()
#                 assert_true(self.home_page.is_home_page(), f"用户 {username} 应该能成功登录")
#         else:
#             with allure.step("验证登录失败"):
#                 assert_true(self.login_page.is_login_page(), f"用户 {username} 登录应该失败")
#                 error_message = self.login_page.get_error_message()
#                 assert_true(len(error_message) > 0, "应该显示错误信息")
#
#     @pytest.mark.parametrize("user_data", [
#         generate_user_data("normal"),
#         generate_user_data("admin"),
#         generate_user_data("vip"),
#     ])
#     @allure.severity(allure.severity_level.MINOR)
#     def test_login_with_generated_users(self, user_data):
#         """使用生成的用户数据测试登录"""
#         allure.dynamic.title(f"生成用户登录测试: {user_data['username']}")
#
#         with allure.step(f"使用生成的用户数据登录: {user_data['username']}"):
#             self.login_page.wait_for_page_load()
#             self.login_page.login(user_data['username'], user_data['password'])
#
#         with allure.step("验证登录结果"):
#             # 由于是随机生成的用户，预期应该登录失败
#             assert_true(self.login_page.is_login_page(), "随机生成的用户应该登录失败")

#
# @allure.epic("用户管理")
# @allure.feature("登录功能")
# @allure.story("登录性能测试")
# class TestLoginPerformance(AndroidTest):
#     """登录性能测试"""
#
#     def setup_method(self, method):
#         """测试方法设置"""
#         super().setup_method(method)
#         self.login_page = PageFactory.create_page("login_page", self.driver)
#         self.home_page = PageFactory.create_page("home_page", self.driver)
#
#     @allure.severity(allure.severity_level.MINOR)
#     def test_login_response_time(self):
#         """测试登录响应时间"""
#         import time
#
#         with allure.step("等待登录页面加载"):
#             self.login_page.wait_for_page_load()
#
#         with allure.step("记录登录开始时间"):
#             start_time = time.time()
#             self.login_page.login("testuser", "test123")
#
#         with allure.step("等待登录完成并记录结束时间"):
#             self.home_page.wait_for_page_load()
#             end_time = time.time()
#
#             response_time = end_time - start_time
#             allure.attach(f"登录响应时间: {response_time:.2f} 秒", name="响应时间",
#                          attachment_type=allure.attachment_type.TEXT)
#
#             # 断言响应时间应该在合理范围内（比如5秒内）
#             assert_true(response_time < 5.0, f"登录响应时间应该小于5秒，实际: {response_time:.2f}秒")
#
#     @allure.severity(allure.severity_level.TRIVIAL)
#     def test_multiple_login_attempts(self):
#         """测试多次登录尝试"""
#         attempt_count = 3
#
#         for i in range(attempt_count):
#             with allure.step(f"第 {i+1} 次登录尝试"):
#                 if i > 0:
#                     # 如果不是第一次，需要先退出登录
#                     if self.home_page.is_home_page():
#                         self.home_page.click_logout()
#                         self.login_page.wait_for_page_load()
#
#                 self.login_page.login("testuser", "test123")
#                 self.home_page.wait_for_page_load()
#                 assert_true(self.home_page.is_home_page(), f"第 {i+1} 次登录应该成功")