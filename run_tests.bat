@echo off
chcp 65001 > nul
echo ======================================
echo UI自动化测试框架 - Windows启动脚本
echo ======================================

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

echo 当前目录: %CD%

if "%1"=="" (
    echo.
    echo 使用方法:
    echo   run_tests.bat check          - 检查测试环境
    echo   run_tests.bat smoke          - 运行冒烟测试
    echo   run_tests.bat regression     - 运行回归测试
    echo   run_tests.bat login          - 运行登录测试
    echo   run_tests.bat home           - 运行主页测试
    echo   run_tests.bat report         - 生成测试报告
    echo   run_tests.bat clean          - 清理测试报告
    echo.
    echo 示例:
    echo   run_tests.bat smoke android
    echo   run_tests.bat run --markers smoke --platform android
    echo.
    pause
    exit /b 1
)

echo 检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo 激活虚拟环境（如果存在）...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo 虚拟环境已激活
) else (
    echo 未找到虚拟环境，使用系统Python
)

echo 执行测试命令: python run_tests.py %*
python run_tests.py %*

if errorlevel 1 (
    echo 测试执行失败
    pause
    exit /b 1
) else (
    echo 测试执行完成
)

pause