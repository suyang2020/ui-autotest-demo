# pytest配置文件
# 导入必要的模块
import pytest
import sys
import allure
from pathlib import Path
from src.utils.report_manager import setup_allure_report
from src.utils.logger import LoggerManager
from src.core import appium_server_manager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """pytest配置hook：在 pytest 开始执行前进行一次性配置"""
    # 设置日志
    LoggerManager.setup_allure_logging()
    
    # 设置Allure报告
    setup_allure_report()
    
    # 清空之前的Allure结果（可选）
    from src.utils.report_manager import allure_manager
    allure_manager.clean_results()
    
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试用例"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试用例"
    )
    config.addinivalue_line(
        "markers", "web: Web UI测试用例"
    )
    config.addinivalue_line(
        "markers", "app: App UI测试用例"
    )
    config.addinivalue_line(
        "markers", "android: Android测试用例"
    )
    config.addinivalue_line(
        "markers", "ios: iOS测试用例"
    )


def pytest_sessionstart(session):
    """测试会话开始，整个测试会话开始时的钩子，用于输出开始信息，可以在这里进行全局初始化"""
    print("\\n" + "="*80)
    print("UI自动化测试开始执行")
    print("="*80)


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束，输出结束信息，可以在这里进行清理工作"""
    print("\\n" + "="*80)
    print("UI自动化测试执行完成")
    print(f"退出状态: {exitstatus}")
    print("="*80)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告，在每个测试步骤（setup/call/teardown）生成报告时调用"""
    outcome = yield
    rep = outcome.get_result()
    
    # 为测试项添加报告属性，用于在teardown中访问
    setattr(item, f"rep_{rep.when}", rep)
    
    # 如果测试失败，添加失败处理逻辑
    if rep.when == "call" and rep.failed:
        # 尝试获取driver并截图
        try:
            # 从测试类实例中获取driver
            if hasattr(item.instance, 'driver') and item.instance.driver:
                # 使用专用的截图管理器
                from src.utils.screenshot import ScreenshotManager
                screenshot_manager = ScreenshotManager(item.instance.driver)
                screenshot_path = screenshot_manager.take_failure_screenshot(item.name)
                
                if screenshot_path:
                    # 读取截图文件并附加到Allure报告
                    with open(screenshot_path, 'rb') as f:
                        allure.attach(
                            f.read(),
                            name="失败截图",
                            attachment_type=allure.attachment_type.PNG
                        )
        except Exception as e:
            # 如果截图失败，记录错误但不影响测试流程
            print(f"截图失败: {e}")


def pytest_collection_modifyitems(config, items):
    """修改收集到的测试项"""
    # 为没有标记的测试添加默认标记
    for item in items:
        if not any(mark.name in ['smoke', 'regression'] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.regression)


# Fixtures
@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """测试环境fixture"""
    from src.config import env_manager
    print(f"\\n当前测试环境: {env_manager.current_env.value}")
    return env_manager.current_env


@pytest.fixture(scope="session")
def ensure_appium_server():
    """确保Appium服务器运行"""
    try:
        if not appium_server_manager.auto_start_server():
            pytest.skip("无法启动Appium服务器")
        yield
        # 保持服务器运行，便于调试
    except Exception as e:
        pytest.skip(f"启动Appium服务器失败: {str(e)}")


@pytest.fixture(autouse=True)
def log_test_info(request):
    """自动记录测试信息"""
    from src.utils import get_logger
    logger = get_logger()
    
    logger.info(f"开始执行测试: {request.node.name}")
    yield
    logger.info(f"测试执行完成: {request.node.name}")


# 命令行选项
def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="测试平台: android 或 ios"
    )
    parser.addoption(
        "--device",
        action="store",
        default=None,
        help="设备名称"
    )
    parser.addoption(
        "--app",
        action="store",
        default=None,
        help="应用路径"
    )
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="测试环境: dev, test, staging, prod"
    )


@pytest.fixture
def platform(request):
    """平台fixture"""
    return request.config.getoption("--platform")


@pytest.fixture
def device_name(request):
    """设备名称fixture"""
    return request.config.getoption("--device")


@pytest.fixture
def app_path(request):
    """应用路径fixture"""
    return request.config.getoption("--app")


@pytest.fixture
def test_env(request):
    """测试环境fixture"""
    return request.config.getoption("--env")