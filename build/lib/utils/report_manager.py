"""
Allure报告配置和管理模块
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from ..config import config
from ..utils import get_logger

logger = get_logger(__name__)


class AllureManager:
    """Allure报告管理器"""
    
    def __init__(self):
        self.allure_config = config.get_allure_config()
        self.results_dir = Path(self.allure_config.get('results_dir', './reports/allure_raw'))
        self.report_dir = Path(self.allure_config.get('report_dir', './reports/allure_report'))
        
        # 确保目录存在
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_results(self):
        """清空Allure结果目录"""
        try:
            if self.results_dir.exists():
                import shutil
                shutil.rmtree(self.results_dir)
                self.results_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"已清空Allure结果目录: {self.results_dir}")
        except Exception as e:
            logger.error(f"清空Allure结果目录失败: {e}")
    
    def generate_report(self, open_browser: bool = False) -> bool:
        """生成Allure报告"""
        try:
            # 检查是否安装了Allure命令行工具
            subprocess.run(['allure', '--version'], 
                          capture_output=True, check=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("未找到Allure命令行工具，请先安装Allure")
            return False
        
        try:
            # 生成报告
            cmd = ['allure', 'generate', str(self.results_dir), '-o', str(self.report_dir), '--clean']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Allure报告生成成功: {self.report_dir}")
            
            # 如果需要，打开浏览器
            if open_browser:
                self.open_report()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"生成Allure报告失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return False
    
    def serve_report(self, port: int = 8080) -> bool:
        """启动Allure服务器"""
        try:
            cmd = ['allure', 'serve', str(self.results_dir), '--port', str(port)]
            logger.info(f"启动Allure服务器，端口: {port}")
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"启动Allure服务器失败: {e}")
            return False
    
    def open_report(self):
        """打开生成的报告"""
        index_file = self.report_dir / 'index.html'
        if index_file.exists():
            import webbrowser
            webbrowser.open(f'file://{index_file.absolute()}')
            logger.info(f"已在浏览器中打开报告: {index_file}")
        else:
            logger.warning("报告文件不存在，请先生成报告")
    
    def add_environment_info(self, env_info: Dict[str, str]):
        """添加环境信息到Allure报告"""
        env_file = self.results_dir / 'environment.properties'
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                for key, value in env_info.items():
                    f.write(f"{key}={value}\\n")
            
            logger.info(f"环境信息已添加到: {env_file}")
        except Exception as e:
            logger.error(f"添加环境信息失败: {e}")
    
    def add_categories(self, categories: List[Dict]):
        """添加测试分类定义"""
        categories_file = self.results_dir / 'categories.json'
        
        try:
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(categories, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试分类已添加到: {categories_file}")
        except Exception as e:
            logger.error(f"添加测试分类失败: {e}")
    
    def get_test_results_summary(self) -> Dict:
        """获取测试结果摘要"""
        try:
            # 这里可以解析Allure结果文件来获取摘要信息
            # 简化实现，返回基本信息
            result_files = list(self.results_dir.glob("*-result.json"))
            
            summary = {
                "total_tests": len(result_files),
                "results_dir": str(self.results_dir),
                "report_dir": str(self.report_dir)
            }
            
            return summary
        except Exception as e:
            logger.error(f"获取测试结果摘要失败: {e}")
            return {}


class ReportConfigurator:
    """报告配置器"""
    
    def __init__(self, allure_manager: AllureManager = None):
        self.allure_manager = allure_manager or AllureManager()
    
    def setup_default_environment(self):
        """设置默认环境信息"""
        from ..config import env_manager
        import platform
        import sys
        
        env_info = {
            "Test.Environment": env_manager.current_env.value,
            "Python.Version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "Platform": platform.platform(),
            "OS": platform.system(),
            "Architecture": platform.machine(),
            "Framework": "ui-autotest",
            "Framework.Version": "0.1.0"
        }
        
        # 添加设备信息
        device_config = config.get_device_config('android')
        if device_config:
            env_info.update({
                "Device.Platform": device_config.get('platformName', 'Unknown'),
                "Device.Version": device_config.get('platformVersion', 'Unknown'),
                "Device.Name": device_config.get('deviceName', 'Unknown'),
            })
        
        self.allure_manager.add_environment_info(env_info)
    
    def setup_default_categories(self):
        """设置默认测试分类"""
        categories = [
            {
                "name": "产品缺陷",
                "matchedStatuses": ["failed"],
                "messageRegex": ".*AssertionError.*"
            },
            {
                "name": "测试缺陷",
                "matchedStatuses": ["broken"],
                "messageRegex": ".*selenium.*|.*appium.*"
            },
            {
                "name": "忽略的测试",
                "matchedStatuses": ["skipped"]
            },
            {
                "name": "基础设施问题",
                "matchedStatuses": ["broken"],
                "messageRegex": ".*Connection.*|.*Timeout.*|.*Server.*"
            },
            {
                "name": "已知问题",
                "matchedStatuses": ["failed"],
                "messageRegex": ".*KNOWN_ISSUE.*"
            }
        ]
        
        self.allure_manager.add_categories(categories)
    
    def setup_all(self):
        """设置所有默认配置"""
        self.setup_default_environment()
        self.setup_default_categories()
        logger.info("Allure报告配置完成")


class HTMLReportGenerator:
    """HTML报告生成器（简单版本）"""
    
    def __init__(self, output_dir: str = "./reports/html"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_simple_report(self, test_results: Dict) -> str:
        """生成简单的HTML报告"""
        html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI自动化测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .summary table {{ border-collapse: collapse; width: 100%; }}
        .summary th, .summary td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .summary th {{ background-color: #4CAF50; color: white; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UI自动化测试报告</h1>
        <p>生成时间: {timestamp}</p>
        <p>测试环境: {environment}</p>
    </div>
    
    <div class="summary">
        <h2>测试结果摘要</h2>
        <table>
            <tr>
                <th>总计</th>
                <th class="passed">通过</th>
                <th class="failed">失败</th>
                <th class="skipped">跳过</th>
                <th>通过率</th>
            </tr>
            <tr>
                <td>{total}</td>
                <td class="passed">{passed}</td>
                <td class="failed">{failed}</td>
                <td class="skipped">{skipped}</td>
                <td>{pass_rate}%</td>
            </tr>
        </table>
    </div>
    
    <div class="details">
        <h2>详细信息</h2>
        <p>更详细的测试结果请查看 Allure 报告。</p>
    </div>
</body>
</html>
        '''
        
        from datetime import datetime
        from ..config import env_manager
        
        # 计算通过率
        total = test_results.get('total', 0)
        passed = test_results.get('passed', 0)
        pass_rate = round((passed / total * 100) if total > 0 else 0, 2)
        
        html_content = html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            environment=env_manager.current_env.value,
            total=total,
            passed=passed,
            failed=test_results.get('failed', 0),
            skipped=test_results.get('skipped', 0),
            pass_rate=pass_rate
        )
        
        report_file = self.output_dir / 'test_report.html'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML报告生成成功: {report_file}")
        return str(report_file)


# 全局实例
allure_manager = AllureManager()
report_configurator = ReportConfigurator(allure_manager)
html_report_generator = HTMLReportGenerator()


# 便捷函数
def setup_allure_report():
    """设置Allure报告的便捷函数"""
    report_configurator.setup_all()


def generate_reports(open_browser: bool = False, include_html: bool = True):
    """生成所有报告的便捷函数"""
    # 生成Allure报告
    allure_success = allure_manager.generate_report(open_browser)
    
    # 生成HTML报告
    html_success = False
    if include_html:
        try:
            summary = allure_manager.get_test_results_summary()
            # 这里可以添加更复杂的结果解析逻辑
            test_results = {
                'total': summary.get('total_tests', 0),
                'passed': 0,  # 需要解析Allure结果获取
                'failed': 0,
                'skipped': 0
            }
            html_report_generator.generate_simple_report(test_results)
            html_success = True
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
    
    return allure_success, html_success