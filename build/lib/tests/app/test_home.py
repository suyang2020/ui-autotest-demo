"""
主页功能测试用例
测试主页面的各种功能
"""
import pytest
import allure
from ..base_test import AndroidTest
from ...pages.page_factory import PageFactory
from ...pages.app import LoginPage, HomePage, CategoryPage, HomePageNavigator
from ...utils import assert_true, assert_equal, take_step_screenshot
from ...utils import log_step

@allure.epic("主要功能")
@allure.feature("主页功能")
class TestHomePage(AndroidTest):
    """主页功能测试类"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
        
        # 先登录到主页
        self._login_to_home()
    
    def _login_to_home(self):
        """登录到主页的辅助方法"""
        self.login_page.wait_for_page_load()
        self.login_page.login("testuser", "test123")
        self.home_page.wait_for_page_load()
    
    @allure.story("主页加载")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_home_page_load(self):
        """测试主页加载"""
        with allure.step("验证主页加载成功"):
            assert_true(self.home_page.is_home_page(), "应该在主页面")
            take_step_screenshot("主页加载成功")
    
    @allure.story("搜索功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_search_functionality(self):
        """测试搜索功能"""
        search_keyword = "测试商品"
        
        with allure.step(f"搜索关键词: {search_keyword}"):
            self.home_page.search(search_keyword)
            take_step_screenshot("执行搜索")
        
        with allure.step("验证搜索执行"):
            # 这里可以添加搜索结果的验证逻辑
            # 比如检查页面是否跳转到搜索结果页，或者内容是否更新
            take_step_screenshot("搜索结果")
    
    @allure.story("搜索功能")
    @allure.severity(allure.severity_level.MINOR)
    def test_clear_search(self):
        """测试清空搜索"""
        with allure.step("先输入搜索内容"):
            self.home_page.search("测试内容")
        
        with allure.step("清空搜索框"):
            self.home_page.clear_search()
            take_step_screenshot("清空搜索框")
        
        with allure.step("验证搜索框已清空"):
            # 这里可以验证搜索框是否为空
            pass
    
    @allure.story("底部导航")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bottom_navigation(self):
        """测试底部导航功能"""
        
        with allure.step("点击分类标签"):
            self.home_page.click_category_tab()
            take_step_screenshot("点击分类标签")
        
        with allure.step("点击购物车标签"):
            self.home_page.click_cart_tab()
            take_step_screenshot("点击购物车标签")
        
        with allure.step("点击个人中心标签"):
            self.home_page.click_profile_tab()
            take_step_screenshot("点击个人中心标签")
        
        with allure.step("返回首页标签"):
            self.home_page.click_home_tab()
            take_step_screenshot("返回首页")
            assert_true(self.home_page.is_home_page(), "应该返回到主页面")
    
    @allure.story("内容浏览")
    @allure.severity(allure.severity_level.NORMAL)
    def test_content_browsing(self):
        """测试内容浏览功能"""
        
        with allure.step("获取内容项数量"):
            initial_count = self.home_page.get_content_items_count()
            allure.attach(f"初始内容项数量: {initial_count}", name="内容数量", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("点击第一个内容项"):
            if initial_count > 0:
                self.home_page.click_content_item(0)
                take_step_screenshot("点击内容项")
            else:
                pytest.skip("没有内容项可点击")
    
    @allure.story("滚动加载")
    @allure.severity(allure.severity_level.MINOR)
    def test_scroll_to_load_more(self):
        """测试滚动加载更多内容"""
        
        with allure.step("获取初始内容数量"):
            initial_count = self.home_page.get_content_items_count()
        
        with allure.step("滚动加载更多内容"):
            self.home_page.scroll_to_load_more(max_scrolls=3)
            take_step_screenshot("滚动加载更多")
        
        with allure.step("验证内容是否增加"):
            final_count = self.home_page.get_content_items_count()
            allure.attach(f"滚动前: {initial_count}, 滚动后: {final_count}", 
                         name="内容数量对比", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("页面刷新")
    @allure.severity(allure.severity_level.MINOR)
    def test_page_refresh(self):
        """测试页面刷新功能"""
        
        with allure.step("执行下拉刷新"):
            self.home_page.refresh_page()
            take_step_screenshot("执行刷新")
        
        with allure.step("验证页面刷新成功"):
            assert_true(self.home_page.is_home_page(), "刷新后应该还在主页面")
    
    @allure.story("返回顶部")
    @allure.severity(allure.severity_level.TRIVIAL)
    def test_go_to_top(self):
        """测试返回顶部功能"""
        
        with allure.step("先滚动到页面底部"):
            self.home_page.scroll_to_load_more(max_scrolls=5)
        
        with allure.step("返回页面顶部"):
            self.home_page.go_to_top()
            take_step_screenshot("返回顶部")
        
        with allure.step("验证已返回顶部"):
            # 可以通过检查标题栏是否可见来验证
            assert_true(self.home_page.is_home_page(), "应该还在主页面")


@allure.epic("主要功能")
@allure.feature("页面导航")
class TestPageNavigation(AndroidTest):
    """页面导航测试类"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
        
        # 先登录到主页
        self._login_to_home()
    
    def _login_to_home(self):
        """登录到主页的辅助方法"""
        self.login_page.wait_for_page_load()
        self.login_page.login("testuser", "test123")
        self.home_page.wait_for_page_load()
    
    @allure.story("页面导航")
    @allure.severity(allure.severity_level.NORMAL)
    def test_navigation_to_category(self):
        """测试导航到分类页面"""
        
        with allure.step("使用导航助手导航到分类页面"):
            navigator = HomePageNavigator(self.home_page)
            category_page = navigator.navigate_to_category()
            take_step_screenshot("导航到分类页面")
        
        with allure.step("验证页面导航成功"):
            # 如果CategoryPage有相应的检查方法
            if hasattr(category_page, 'wait_for_page_load'):
                category_page.wait_for_page_load()
    
    @allure.story("用户操作")
    @allure.severity(allure.severity_level.MINOR)
    def test_user_avatar_click(self):
        """测试点击用户头像"""
        
        with allure.step("点击用户头像"):
            self.home_page.click_user_avatar()
            take_step_screenshot("点击用户头像")
        
        with allure.step("验证点击响应"):
            # 这里可以验证是否打开了用户菜单或跳转到用户页面
            pass
    
    @allure.story("设置功能")
    @allure.severity(allure.severity_level.MINOR)
    def test_settings_access(self):
        """测试访问设置功能"""
        
        with allure.step("点击设置按钮"):
            self.home_page.click_settings()
            take_step_screenshot("点击设置")
        
        with allure.step("验证设置页面打开"):
            # 这里可以验证是否打开了设置页面
            pass


@allure.epic("主要功能")
@allure.feature("分类页面")
class TestCategoryPage(AndroidTest):
    """分类页面测试类"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
        self.category_page = PageFactory.create_page("category_page", self.driver)
        
        # 先登录并导航到分类页面
        self._navigate_to_category()
    
    def _navigate_to_category(self):
        """导航到分类页面的辅助方法"""
        self.login_page.wait_for_page_load()
        self.login_page.login("testuser", "test123")
        self.home_page.wait_for_page_load()
        self.home_page.click_category_tab()
        self.category_page.wait_for_page_load()
    
    @allure.story("分类列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_category_list_display(self):
        """测试分类列表显示"""
        
        with allure.step("获取分类列表"):
            categories = self.category_page.get_categories()
            take_step_screenshot("分类列表")
        
        with allure.step("验证分类列表"):
            assert_true(len(categories) > 0, "应该有分类显示")
            allure.attach(f"分类数量: {len(categories)}", name="分类信息", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach("\\n".join(categories), name="分类列表", 
                         attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("分类点击")
    @allure.severity(allure.severity_level.NORMAL)
    def test_category_click(self):
        """测试点击分类"""
        
        with allure.step("获取分类列表"):
            categories = self.category_page.get_categories()
        
        if categories:
            with allure.step(f"点击第一个分类: {categories[0]}"):
                self.category_page.click_category(categories[0])
                take_step_screenshot(f"点击分类_{categories[0]}")
            
            with allure.step("验证子分类显示"):
                subcategories = self.category_page.get_subcategories()
                allure.attach(f"子分类数量: {len(subcategories)}", name="子分类信息", 
                             attachment_type=allure.attachment_type.TEXT)
        else:
            pytest.skip("没有分类可点击")


# 性能相关测试
@allure.epic("性能测试")
@allure.feature("主页性能")
class TestHomePagePerformance(AndroidTest):
    """主页性能测试"""
    
    def setup_method(self, method):
        """测试方法设置"""
        super().setup_method(method)
        self.login_page = PageFactory.create_page("login_page", self.driver)
        self.home_page = PageFactory.create_page("home_page", self.driver)
        
        # 先登录到主页
        self._login_to_home()
    
    def _login_to_home(self):
        """登录到主页的辅助方法"""
        self.login_page.wait_for_page_load()
        self.login_page.login("testuser", "test123")
        self.home_page.wait_for_page_load()
    
    @allure.story("页面加载性能")
    @allure.severity(allure.severity_level.MINOR)
    def test_home_page_load_time(self):
        """测试主页加载时间"""
        import time
        
        with allure.step("刷新页面并测量加载时间"):
            start_time = time.time()
            self.home_page.refresh_page()
            self.home_page.wait_for_page_load()
            end_time = time.time()
            
            load_time = end_time - start_time
            allure.attach(f"页面加载时间: {load_time:.2f} 秒", name="加载时间", 
                         attachment_type=allure.attachment_type.TEXT)
            
            # 断言加载时间应该在合理范围内
            assert_true(load_time < 10.0, f"页面加载时间应该小于10秒，实际: {load_time:.2f}秒")
    
    @allure.story("搜索性能")
    @allure.severity(allure.severity_level.TRIVIAL)
    def test_search_response_time(self):
        """测试搜索响应时间"""
        import time
        
        with allure.step("执行搜索并测量响应时间"):
            start_time = time.time()
            self.home_page.search("性能测试")
            # 这里需要等待搜索结果显示，具体实现取决于应用
            time.sleep(2)  # 简单等待
            end_time = time.time()
            
            response_time = end_time - start_time
            allure.attach(f"搜索响应时间: {response_time:.2f} 秒", name="响应时间", 
                         attachment_type=allure.attachment_type.TEXT)
            
            assert_true(response_time < 5.0, f"搜索响应时间应该小于5秒，实际: {response_time:.2f}秒")