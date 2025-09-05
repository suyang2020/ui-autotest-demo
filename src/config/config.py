"""
配置管理模块
负责管理测试环境配置、设备配置、服务器配置等
"""
import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """配置管理类，使用单例模式"""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config_data is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config_file = self._find_config_file()
        if config_file.suffix == '.yaml' or config_file.suffix == '.yml':
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f)
        elif config_file.suffix == '.json':
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_file}")
    
    def _find_config_file(self) -> Path:
        """查找配置文件"""
        project_root = Path(__file__).parent.parent.parent
        config_files = [
            project_root / 'config.yaml',
            project_root / 'config.yml', 
            project_root / 'config.json',
            project_root / 'src' / 'config' / 'config.yaml',
            project_root / 'src' / 'config' / 'config.yml',
            project_root / 'src' / 'config' / 'config.json'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                return config_file
        
        # 如果没有找到配置文件，创建默认配置
        default_config = project_root / 'config.yaml'
        self._create_default_config(default_config)
        return default_config
    
    def _create_default_config(self, config_file: Path):
        """创建默认配置文件"""
        default_config = {
            'appium': {
                'server_url': 'http://localhost:4723/wd/hub',
                'timeout': 30
            },
            'devices': {
                'android': {
                    'platformName': 'Android',
                    'automationName': 'UiAutomator2',
                    'deviceName': 'emulator-5554',
                    'platformVersion': '11.0',
                    'app': None,
                    'appPackage': None,
                    'appActivity': None,
                    'noReset': True,
                    'fullReset': False,
                    'unicodeKeyboard': True,
                    'resetKeyboard': True
                },
                'ios': {
                    'platformName': 'iOS',
                    'automationName': 'XCUITest',
                    'deviceName': 'iPhone 13',
                    'platformVersion': '15.0',
                    'app': None,
                    'bundleId': None,
                    'noReset': True,
                    'fullReset': False
                }
            },
            'test': {
                'default_timeout': 10,
                'implicit_wait': 5,
                'screenshot_on_failure': True,
                'screenshot_dir': './reports/screenshots',
                'log_level': 'INFO'
            },
            'allure': {
                'results_dir': './reports/allure_raw',
                'report_dir': './reports/allure_report'
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, 
                     allow_unicode=True, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        data = self._config_data
        
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        
        return data
    
    def get_appium_config(self) -> Dict[str, Any]:
        """获取Appium服务器配置"""
        return self.get('appium', {})
    
    def get_device_config(self, platform: str = 'android') -> Dict[str, Any]:
        """获取设备配置"""
        return self.get(f'devices.{platform}', {})
    
    def get_test_config(self) -> Dict[str, Any]:
        """获取测试配置"""
        return self.get('test', {})
    
    def get_allure_config(self) -> Dict[str, Any]:
        """获取Allure配置"""
        return self.get('allure', {})
    
    def update_config(self, key: str, value: Any):
        """更新配置项"""
        keys = key.split('.')
        data = self._config_data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value


# 全局配置实例
config = Config()