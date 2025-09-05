#!/bin/bash

echo "======================================"
echo "UI自动化测试框架 - Linux/Mac启动脚本"
echo "======================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "当前目录: $(pwd)"

if [ $# -eq 0 ]; then
    echo ""
    echo "使用方法:"
    echo "  ./run_tests.sh check          - 检查测试环境"
    echo "  ./run_tests.sh smoke          - 运行冒烟测试"
    echo "  ./run_tests.sh regression     - 运行回归测试"
    echo "  ./run_tests.sh login          - 运行登录测试"
    echo "  ./run_tests.sh home           - 运行主页测试"
    echo "  ./run_tests.sh report         - 生成测试报告"
    echo "  ./run_tests.sh clean          - 清理测试报告"
    echo ""
    echo "示例:"
    echo "  ./run_tests.sh smoke android"
    echo "  ./run_tests.sh run --markers smoke --platform android"
    echo ""
    exit 1
fi

echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python，请确保Python已安装"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python命令: $PYTHON_CMD"
$PYTHON_CMD --version

echo "激活虚拟环境（如果存在）..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "虚拟环境已激活"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "虚拟环境已激活"
else
    echo "未找到虚拟环境，使用系统Python"
fi

echo "执行测试命令: $PYTHON_CMD run_tests.py $@"
$PYTHON_CMD run_tests.py "$@"

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "测试执行失败，退出码: $exit_code"
    exit $exit_code
else
    echo "测试执行完成"
fi