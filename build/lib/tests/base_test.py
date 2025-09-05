"""
测试基类
为所有测试用例提供基础功能
"""
import pytest
import allure
from appium.webdriver.webdriver import WebDriver
from ...core import driver_manager, appium_server_manager, DriverFactory
from ...config import config, env_manager
from ...utils import get_logger, take_failure_screenshot, ScreenshotDecorator
from ...pages.page_factory import PageFactory, PageNavigator

logger = get_logger(__name__)


class BaseTest:
    """测试基类"""
    
    driver: WebDriver = None
    page_navigator: PageNavigator = None
    
    @classmethod
    def setup_class(cls):
        """类级别设置"""
        logger.info(f"开始执行测试类: {cls.__name__}")
        
        # 确保Appium服务器运行
        if not appium_server_manager.ensure_server_running():
            pytest.skip("Appium服务器启动失败")
    
    def setup_method(self, method):
        """方法级别设置"""
        logger.info(f"开始执行测试方法: {method.__name__}")
        
        # 创建WebDriver实例
        try:
            self.driver = DriverFactory.create_android_driver()
            self.page_navigator = PageNavigator(self.driver)
            logger.info("WebDriver创建成功")
        except Exception as e:
            logger.error(f"WebDriver创建失败: {e}")
            pytest.fail(f"无法创建WebDriver: {e}")
    
    def teardown_method(self, method):
        """方法级别清理"""
        logger.info(f"结束执行测试方法: {method.__name__}")
        
        # 清理页面实例缓存
        PageFactory.clear_page_instances()
        
        # 退出WebDriver
        if self.driver:
            try:
                driver_manager.quit_driver()
                logger.info("WebDriver已退出")
            except Exception as e:
                logger.warning(f"退出WebDriver时出错: {e}")
    
    @classmethod
    def teardown_class(cls):
        """类级别清理"""
        logger.info(f"结束执行测试类: {cls.__name__}")
        
        # 清理所有驱动
        driver_manager.quit_all_drivers()
    
    def take_screenshot(self, description: str = None):
        """截图"""
        if self.driver:
            return take_failure_screenshot(description or "测试截图")
        return ""
    
    @pytest.fixture(autouse=True)
    def auto_screenshot_on_failure(self, request):
        """失败时自动截图"""
        yield
        
        if request.node.rep_call.failed:
            screenshot_path = self.take_screenshot(f"失败_{request.node.name}")
            if screenshot_path:
                logger.error(f"测试失败截图: {screenshot_path}")
                
                # 添加到Allure报告
                try:
                    with open(screenshot_path, 'rb') as f:
                        allure.attach(f.read(), name="失败截图", attachment_type=allure.attachment_type.PNG)
                except:
                    pass
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """用于获取测试结果的hook"""
        outcome = yield
        rep = outcome.get_result()
        setattr(item, f"rep_{rep.when}", rep)


class AndroidTest(BaseTest):
    """Android测试基类"""
    
    def setup_method(self, method):
        """Android特定设置"""
        super().setup_method(method)
        
        # Android特定配置
        if self.driver:
            # 设置隐式等待
            self.driver.implicitly_wait(config.get_test_config().get('implicit_wait', 5))
            
            # 启用Unicode键盘（如果配置了）
            device_config = config.get_device_config('android')
            if device_config.get('unicodeKeyboard'):
                try:
                    self.driver.execute_script('mobile: shell', {
                        'command': 'settings put secure default_input_method io.appium.settings/.UnicodeIME'
                    })
                except Exception as e:
                    logger.debug(f"设置Unicode键盘失败: {e}")


class IOSTest(BaseTest):
    """iOS测试基类"""
    
    def setup_method(self, method):
        """iOS特定设置"""
        # 创建iOS驱动
        try:
            self.driver = DriverFactory.create_ios_driver()
            self.page_navigator = PageNavigator(self.driver)
            logger.info("iOS WebDriver创建成功")
        except Exception as e:
            logger.error(f"iOS WebDriver创建失败: {e}")
            pytest.skip(f"无法创建iOS WebDriver: {e}")


# Pytest fixtures
@pytest.fixture(scope="session")
def appium_server():
    """Appium服务器fixture"""
    if not appium_server_manager.ensure_server_running():
        pytest.skip("无法启动Appium服务器")
    yield
    # 测试结束后保持服务器运行，便于调试


@pytest.fixture(scope="function")
def android_driver():
    """Android驱动fixture"""
    driver = DriverFactory.create_android_driver()
    yield driver
    driver_manager.quit_driver()


@pytest.fixture(scope="function")
def ios_driver():
    """iOS驱动fixture"""
    try:
        driver = DriverFactory.create_ios_driver()
        yield driver
    except Exception as e:
        pytest.skip(f"无法创建iOS驱动: {e}")
    finally:
        driver_manager.quit_driver()


@pytest.fixture(scope="function")
def page_navigator_fixture(android_driver):
    """页面导航器fixture"""
    navigator = PageNavigator(android_driver)
    yield navigator
    PageFactory.clear_page_instances()