"""
主页面对象
应用主页面的页面对象模型
"""
from typing import List
from appium.webdriver.common.appiumby import AppiumBy
from ..base_page import BasePage, ElementLocators
from ..page_factory import page_register
from ...utils import get_logger, log_step

logger = get_logger(__name__)


@page_register("home_page")
class HomePage(BasePage):
    """主页面"""
    
    # 顶部导航栏
    TITLE_BAR = ElementLocators.android_id("com.example.app:id/title_bar")
    USER_AVATAR = ElementLocators.android_id("com.example.app:id/user_avatar")
    SETTINGS_BUTTON = ElementLocators.android_id("com.example.app:id/settings_btn")
    LOGOUT_BUTTON = ElementLocators.android_id("com.example.app:id/logout_btn")
    
    # 搜索框
    SEARCH_INPUT = ElementLocators.android_id("com.example.app:id/search_input")
    SEARCH_BUTTON = ElementLocators.android_id("com.example.app:id/search_btn")
    
    # 底部导航栏
    TAB_HOME = ElementLocators.android_id("com.example.app:id/tab_home")
    TAB_CATEGORY = ElementLocators.android_id("com.example.app:id/tab_category")
    TAB_CART = ElementLocators.android_id("com.example.app:id/tab_cart")
    TAB_PROFILE = ElementLocators.android_id("com.example.app:id/tab_profile")
    
    # 内容区域
    CONTENT_LIST = ElementLocators.android_id("com.example.app:id/content_list")
    ITEM_TEMPLATE = ElementLocators.android_xpath("//android.widget.LinearLayout[@resource-id='com.example.app:id/item_layout']")
    
    # 替代定位器
    TITLE_BAR_ALT = ElementLocators.android_xpath("//android.widget.TextView[@text='首页']")
    SEARCH_INPUT_ALT = ElementLocators.android_xpath("//android.widget.EditText[@hint='搜索']")
    
    def __init__(self, driver=None):
        super().__init__(driver)
        self.page_name = "主页面"
    
    @log_step("等待主页面加载")
    def wait_for_page_load(self, timeout: int = 15):
        """等待主页面加载完成"""
        try:
            self.wait_for_element_visible(self.TITLE_BAR, timeout)
            logger.info("主页面加载完成")
        except Exception:
            self.wait_for_element_visible(self.TITLE_BAR_ALT, timeout)
            logger.info("主页面加载完成（使用替代定位器）")
    
    def is_home_page(self) -> bool:
        """检查是否为主页面"""
        return (self.is_element_present(self.TITLE_BAR) or 
                self.is_element_present(self.TITLE_BAR_ALT))
    
    # 顶部导航操作
    def click_user_avatar(self):
        """点击用户头像"""
        self.click(self.USER_AVATAR)
        logger.info("点击用户头像")
    
    def click_settings(self):
        """点击设置按钮"""
        self.click(self.SETTINGS_BUTTON)
        logger.info("点击设置按钮")
    
    def click_logout(self):
        """点击退出登录"""
        self.click(self.LOGOUT_BUTTON)
        logger.info("点击退出登录")
    
    # 搜索功能
    @log_step("执行搜索")
    def search(self, keyword: str):
        """执行搜索"""
        try:
            self.send_keys(self.SEARCH_INPUT, keyword)
        except Exception:
            self.send_keys(self.SEARCH_INPUT_ALT, keyword)
        
        self.click(self.SEARCH_BUTTON)
        logger.info(f"搜索关键词: {keyword}")
    
    def clear_search(self):
        """清空搜索框"""
        try:
            self.clear_text(self.SEARCH_INPUT)
        except Exception:
            self.clear_text(self.SEARCH_INPUT_ALT)
        logger.info("清空搜索框")
    
    # 底部导航操作
    def click_home_tab(self):
        """点击首页标签"""
        self.click(self.TAB_HOME)
        logger.info("点击首页标签")
    
    def click_category_tab(self):
        """点击分类标签"""
        self.click(self.TAB_CATEGORY)
        logger.info("点击分类标签")
    
    def click_cart_tab(self):
        """点击购物车标签"""
        self.click(self.TAB_CART)
        logger.info("点击购物车标签")
    
    def click_profile_tab(self):
        """点击个人中心标签"""
        self.click(self.TAB_PROFILE)
        logger.info("点击个人中心标签")
    
    # 内容操作
    def get_content_items_count(self) -> int:
        """获取内容项数量"""
        items = self.find_elements(self.ITEM_TEMPLATE)
        count = len(items)
        logger.info(f"内容项数量: {count}")
        return count
    
    def click_content_item(self, index: int = 0):
        """点击指定内容项"""
        items = self.find_elements(self.ITEM_TEMPLATE)
        if 0 <= index < len(items):
            items[index].click()
            logger.info(f"点击第 {index + 1} 个内容项")
        else:
            logger.warning(f"内容项索引 {index} 超出范围")
    
    def scroll_to_load_more(self, max_scrolls: int = 5):
        """滚动加载更多内容"""
        for i in range(max_scrolls):
            initial_count = self.get_content_items_count()
            self.swipe_up()
            import time
            time.sleep(1)  # 等待加载
            
            new_count = self.get_content_items_count()
            if new_count > initial_count:
                logger.info(f"加载了更多内容，新增 {new_count - initial_count} 项")
            else:
                logger.info("没有更多内容可加载")
                break
    
    # 手势操作
    def refresh_page(self):
        """下拉刷新页面"""
        self.swipe_down()
        logger.info("执行下拉刷新")
        import time
        time.sleep(2)  # 等待刷新完成
    
    def go_to_top(self):
        """返回顶部"""
        for _ in range(10):  # 最多滚动10次
            try:
                if self.is_element_visible(self.TITLE_BAR, timeout=1):
                    break
            except:
                pass
            self.swipe_down()
        logger.info("返回页面顶部")


@page_register("category_page")
class CategoryPage(BasePage):
    """分类页面"""
    
    # 分类列表
    CATEGORY_LIST = ElementLocators.android_id("com.example.app:id/category_list")
    CATEGORY_ITEM = ElementLocators.android_xpath("//android.widget.TextView[@resource-id='com.example.app:id/category_name']")
    
    # 子分类
    SUBCATEGORY_LIST = ElementLocators.android_id("com.example.app:id/subcategory_list")
    SUBCATEGORY_ITEM = ElementLocators.android_xpath("//android.widget.TextView[@resource-id='com.example.app:id/subcategory_name']")
    
    def __init__(self, driver=None):
        super().__init__(driver)
        self.page_name = "分类页面"
    
    def wait_for_page_load(self, timeout: int = 15):
        """等待分类页面加载"""
        self.wait_for_element_visible(self.CATEGORY_LIST, timeout)
        logger.info("分类页面加载完成")
    
    def get_categories(self) -> List[str]:
        """获取所有分类名称"""
        category_elements = self.find_elements(self.CATEGORY_ITEM)
        categories = [element.text for element in category_elements]
        logger.info(f"获取到 {len(categories)} 个分类")
        return categories
    
    def click_category(self, category_name: str):
        """点击指定分类"""
        category_locator = ElementLocators.android_xpath(
            f"//android.widget.TextView[@resource-id='com.example.app:id/category_name' and @text='{category_name}']"
        )
        self.click(category_locator)
        logger.info(f"点击分类: {category_name}")
    
    def get_subcategories(self) -> List[str]:
        """获取子分类列表"""
        subcategory_elements = self.find_elements(self.SUBCATEGORY_ITEM)
        subcategories = [element.text for element in subcategory_elements]
        logger.info(f"获取到 {len(subcategories)} 个子分类")
        return subcategories


# 页面导航助手
class HomePageNavigator:
    """主页面导航助手"""
    
    def __init__(self, home_page: HomePage):
        self.home_page = home_page
    
    def navigate_to_category(self):
        """导航到分类页面"""
        self.home_page.click_category_tab()
        # 这里可以返回CategoryPage实例
        from ..page_factory import PageFactory
        return PageFactory.get_page("category_page")
    
    def navigate_to_cart(self):
        """导航到购物车页面"""
        self.home_page.click_cart_tab()
        # 这里可以返回CartPage实例（如果有的话）
    
    def navigate_to_profile(self):
        """导航到个人中心页面"""
        self.home_page.click_profile_tab()
        # 这里可以返回ProfilePage实例（如果有的话）