"""
环境管理模块
管理不同环境的配置（开发、测试、生产等）
"""
import os
from enum import Enum
from typing import Dict, Any


class Environment(Enum):
    """环境枚举"""
    DEV = "dev"
    TEST = "test"
    STAGING = "staging"
    PROD = "prod"


class EnvironmentManager:
    """环境管理器"""
    
    def __init__(self):
        self.current_env = self._get_current_environment()
        self.env_configs = self._load_environment_configs()
    
    def _get_current_environment(self) -> Environment:
        """获取当前环境"""
        env_name = os.getenv('TEST_ENV', 'test').lower()
        try:
            return Environment(env_name)
        except ValueError:
            print(f"未知环境: {env_name}, 使用默认环境: test")
            return Environment.TEST
    
    def _load_environment_configs(self) -> Dict[Environment, Dict[str, Any]]:
        """加载环境配置"""
        return {
            Environment.DEV: {
                'app_server': 'http://dev-server:8080',
                'database_url': 'dev-db:5432',
                'log_level': 'DEBUG',
                'timeout_multiplier': 2.0,
                'retry_count': 3
            },
            Environment.TEST: {
                'app_server': 'http://test-server:8080',
                'database_url': 'test-db:5432',
                'log_level': 'INFO',
                'timeout_multiplier': 1.0,
                'retry_count': 2
            },
            Environment.STAGING: {
                'app_server': 'http://staging-server:8080',
                'database_url': 'staging-db:5432',
                'log_level': 'INFO',
                'timeout_multiplier': 1.0,
                'retry_count': 1
            },
            Environment.PROD: {
                'app_server': 'http://prod-server:8080',
                'database_url': 'prod-db:5432',
                'log_level': 'WARNING',
                'timeout_multiplier': 0.8,
                'retry_count': 1
            }
        }
    
    def get_config(self, key: str = None) -> Any:
        """获取当前环境配置"""
        env_config = self.env_configs.get(self.current_env, {})
        if key:
            return env_config.get(key)
        return env_config
    
    def set_environment(self, env: Environment):
        """设置当前环境"""
        self.current_env = env
        os.environ['TEST_ENV'] = env.value
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.current_env == Environment.PROD
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.current_env == Environment.DEV


# 全局环境管理器实例
env_manager = EnvironmentManager()