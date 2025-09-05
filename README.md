# UI自动化测试框架

一个功能强大、易于使用的Web + App UI自动化测试框架，基于Selenium/Appium + Pytest + Allure构建。

## 🚀 特性

- **多平台支持**: 支持Android、iOS和Web平台的UI自动化测试
- **页面对象模型**: 采用POM设计模式，提高代码复用性和可维护性
- **数据驱动测试**: 支持JSON、YAML、CSV等多种数据格式
- **丰富的报告**: 集成Allure报告，提供详细的测试结果分析
- **失败截图**: 自动截图功能，便于问题定位
- **并行执行**: 支持多进程并行执行测试，提高测试效率
- **CI/CD集成**: 提供GitHub Actions和Jenkins Pipeline配置
- **环境管理**: 支持多环境配置（开发、测试、生产等）

## 📋 系统要求

- Python 3.10+
- Node.js 14+ (用于Appium)
- Java 8+ (用于Appium和Allure)
- Android SDK (Android测试)
- Appium-inspector 
- appium server

## 🛠️ 安装指南

### 1. 克隆项目

```bash
git clone <repository-url>
cd ui-autotest-demo
```

### 2. 创建Python虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 4. 安装Appium

```bash
npm install -g appium@next
appium driver install uiautomator2  # Android
appium driver install xcuitest      # iOS
```

### 5. 安装Allure命令行工具

#### Windows (使用Scoop)
```bash
scoop install allure
```

#### Mac (使用Homebrew)
```bash
brew install allure
```

#### Linux
```bash
curl -o allure-2.20.1.tgz -Ls https://github.com/allure-framework/allure2/releases/download/2.20.1/allure-2.20.1.tgz
tar -zxf allure-2.20.1.tgz
sudo mv allure-2.20.1 /opt/allure
sudo ln -s /opt/allure/bin/allure /usr/bin/allure
```

### 6. 配置Android环境（可选）

1. 安装Android Studio
2. 配置Android SDK
3. 设置环境变量:
   ```bash
   export ANDROID_HOME=/path/to/android-sdk
   export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
   ```
4. 启动Android模拟器或连接真机

## 🎯 快速开始

### 1. 检查环境

```bash
python run_tests.py check
```

### 2. 运行冒烟测试

```bash
# Windows
run_tests.bat smoke

# Linux/Mac
./run_tests.sh smoke

# 或直接使用Python
python run_tests.py smoke
```

### 3. 查看测试报告

测试完成后，报告会自动在浏览器中打开，或者手动打开：
```bash
python run_tests.py report
```

## 📖 使用指南

### 项目结构

```
ui-autotest/
├── src/                     # 源代码目录
│   ├── config/             # 配置管理
│   │   ├── config.py       # 配置类
│   │   └── environment.py  # 环境管理
│   ├── core/               # 核心功能
│   │   ├── driver_manager.py   # 驱动管理
│   │   └── appium_server.py    # Appium服务器管理
│   ├── pages/              # 页面对象
│   │   ├── base_page.py    # 基础页面类
│   │   ├── page_factory.py # 页面工厂
│   │   └── app/            # App页面对象
│   ├── tests/              # 测试用例
│   │   ├── base_test.py    # 测试基类
│   │   ├── app/            # App测试用例
│   │   └── data/           # 测试数据
│   └── utils/              # 工具类
│       ├── logger.py       # 日志管理
│       ├── assertions.py   # 断言工具
│       ├── screenshot.py   # 截图工具
│       ├── data_manager.py # 数据管理
│       └── report_manager.py # 报告管理
├── reports/                # 测试报告
├── logs/                   # 日志文件
├── config.yaml            # 配置文件
├── conftest.py            # pytest配置
├── run_tests.py           # 测试运行脚本
├── requirements.txt       # Python依赖
└── README.md              # 项目文档
```

### 配置文件

项目会在首次运行时自动创建`config.yaml`配置文件：

```yaml
appium:
  server_url: http://localhost:4723/wd/hub
  timeout: 30

devices:
  android:
    platformName: Android
    automationName: UiAutomator2
    deviceName: emulator-5554
    platformVersion: '11.0'
    # app: /path/to/your/app.apk
    # appPackage: com.example.app
    # appActivity: .MainActivity
  
  ios:
    platformName: iOS
    automationName: XCUITest
    deviceName: iPhone 13
    platformVersion: '15.0'
    # app: /path/to/your/app.app
    # bundleId: com.example.app

test:
  default_timeout: 10
  implicit_wait: 5
  screenshot_on_failure: true
  screenshot_dir: ./reports/screenshots
  log_level: INFO

allure:
  results_dir: ./reports/allure_raw
  report_dir: ./reports/allure_report
```

### 编写测试用例

#### 1. 创建页面对象

```python
from src.pages.base_page import BasePage, ElementLocators
from src.pages.page_factory import page_register

@page_register("my_page")
class MyPage(BasePage):
    # 定义页面元素
    USERNAME_INPUT = ElementLocators.android_id("com.example:id/username")
    LOGIN_BUTTON = ElementLocators.android_id("com.example:id/login")
    
    def enter_username(self, username):
        self.send_keys(self.USERNAME_INPUT, username)
    
    def click_login(self):
        self.click(self.LOGIN_BUTTON)
```

#### 2. 编写测试用例

```python
import pytest
import allure
from src.tests.base_test import AndroidTest
from src.pages.page_factory import PageFactory
from src.utils import assert_true

@allure.epic("用户功能")
@allure.feature("登录")
class TestLogin(AndroidTest):
    
    def setup_method(self, method):
        super().setup_method(method)
        self.my_page = PageFactory.create_page("my_page", self.driver)
    
    @allure.story("正常登录")
    @pytest.mark.smoke
    def test_valid_login(self):
        with allure.step("输入用户名"):
            self.my_page.enter_username("testuser")
        
        with allure.step("点击登录"):
            self.my_page.click_login()
        
        with allure.step("验证登录成功"):
            assert_true(True, "登录成功")
```

### 运行测试

#### 命令行方式

```bash
# 运行所有测试
python run_tests.py run

# 运行特定标记的测试
python run_tests.py run --markers smoke

# 运行特定测试文件
python run_tests.py run --path src/tests/app/test_login.py

# 指定平台和设备
python run_tests.py run --platform android --device emulator-5554

# 并行执行
python run_tests.py run --parallel 2

# 详细输出
python run_tests.py run --verbose
```

#### 预定义命令

```bash
# 冒烟测试
python run_tests.py smoke

# 回归测试
python run_tests.py regression

# 登录功能测试
python run_tests.py login

# 主页功能测试
python run_tests.py home
```

#### 直接使用pytest

```bash
# 基本运行
pytest src/tests/

# 运行特定标记
pytest -m smoke src/tests/

# 生成Allure报告
pytest --alluredir=reports/allure_raw src/tests/
allure serve reports/allure_raw
```

### 测试报告

#### Allure报告

```bash
# 生成并打开Allure报告
python run_tests.py report

# 启动Allure服务器
allure serve reports/allure_raw
```

#### HTML报告

简化版的HTML报告会自动生成在`reports/html/test_report.html`

### 环境变量

可以通过环境变量控制测试行为：

```bash
# 设置测试环境
export TEST_ENV=staging

# 设置日志级别
export LOG_LEVEL=DEBUG

# 设置Appium服务器地址
export APPIUM_SERVER_URL=http://remote-server:4723/wd/hub
```

## 🔧 高级配置

### 多环境支持

框架支持多环境配置，通过`TEST_ENV`环境变量或命令行参数控制：

- `dev`: 开发环境
- `test`: 测试环境（默认）
- `staging`: 预发布环境
- `prod`: 生产环境

### 自定义页面对象

使用页面工厂模式和装饰器注册页面：

```python
from src.pages.page_factory import page_register

@page_register("custom_page")
class CustomPage(BasePage):
    pass

# 使用页面
page = PageFactory.create_page("custom_page", driver)
```

### 数据驱动测试

支持多种数据格式：

```python
from src.utils import get_test_data

# JSON数据
test_data = get_test_data("test_data.json", "login_users")

# YAML数据
test_data = get_test_data("test_data.yaml", "users")

# CSV数据
test_data = get_test_data("users.csv")

# 参数化测试
@pytest.mark.parametrize("username,password", test_data)
def test_login(username, password):
    pass
```

### 自定义断言

```python
from src.utils import Assert, ElementAssert

# 基础断言
Assert.equal(actual, expected)
Assert.true(condition)
Assert.contains(container, item)

# 元素断言
element_assert = ElementAssert(driver)
element_assert.element_present(locator)
element_assert.element_text_equal(locator, "expected text")
```

## 🚀 CI/CD集成

### GitHub Actions

项目已包含GitHub Actions配置文件`.github/workflows/ui-tests.yml`，支持：

- 推送和PR触发
- 定时执行
- 手动触发
- 多Python版本测试
- 自动报告发布

### Jenkins

使用提供的`Jenkinsfile`配置Jenkins Pipeline：

1. 创建新的Pipeline任务
2. 选择"Pipeline script from SCM"
3. 配置Git仓库
4. 指定Jenkinsfile路径

## 🛠️ 故障排除

### 常见问题

#### 1. Appium服务器连接失败

```bash
# 检查Appium服务器是否运行
curl http://localhost:4723/wd/hub/status

# 手动启动Appium服务器
appium --relaxed-security
```

#### 2. 找不到设备

```bash
# 检查连接的设备
adb devices  # Android
instruments -s devices  # iOS
```

#### 3. 元素定位失败

- 检查元素定位器是否正确
- 增加等待时间
- 使用Appium Inspector检查元素属性

#### 4. 权限问题

```bash
# Android权限
adb shell pm grant <package_name> <permission>

# 文件权限
chmod +x run_tests.sh
```

### 调试技巧

1. **启用详细日志**：设置`log_level: DEBUG`
2. **使用截图**：失败时会自动截图
3. **Appium Inspector**：可视化元素定位
4. **逐步调试**：使用pytest的`-s`参数显示输出

## 📚 最佳实践

### 测试用例设计

1. **单一职责**：每个测试用例只测试一个功能点
2. **独立性**：测试用例之间不应有依赖关系
3. **数据驱动**：使用外部数据文件提高测试覆盖率
4. **异常处理**：考虑各种异常情况

### 页面对象设计

1. **封装性**：隐藏页面实现细节
2. **复用性**：提取公共操作到基类
3. **可维护性**：使用有意义的方法名和注释
4. **稳定性**：使用相对稳定的定位器

### 测试数据管理

1. **分离关注点**：测试代码和测试数据分离
2. **环境隔离**：不同环境使用不同的测试数据
3. **数据清理**：测试前后清理测试数据
4. **敏感信息**：使用环境变量存储敏感信息

### 报告和日志

1. **详细信息**：提供足够的上下文信息
2. **分类标记**：使用pytest标记分类测试
3. **截图时机**：关键步骤和失败时截图
4. **日志级别**：合理使用不同的日志级别

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 📞 支持

如果您在使用过程中遇到问题，可以通过以下方式获取支持：

- 提交Issue
- 查看文档
- 参考示例代码

## 🙏 致谢

感谢以下开源项目的支持：

- [Selenium](https://selenium.dev/)
- [Appium](https://appium.io/)
- [Pytest](https://pytest.org/)
- [Allure](https://qameta.io/allure/)
