"""
日志管理模块
提供统一的日志记录功能
"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..config import config


class LoggerManager:
    """日志管理器"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str = None, level: str = None) -> logging.Logger:
        """获取日志器"""
        name = name or 'ui-autotest'
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # 设置日志级别
        level = level or config.get_test_config().get('log_level', 'INFO')
        logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加处理器
        if not logger.handlers:
            cls._setup_logger(logger)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def _setup_logger(cls, logger: logging.Logger):
        """设置日志器"""
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 当前日期的日志文件
        log_file = log_dir / f"test_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 错误日志文件
        error_log_file = log_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    @classmethod
    def setup_allure_logging(cls):
        """设置Allure日志"""
        try:
            import allure
            
            class AllureLogHandler(logging.Handler):
                def emit(self, record):
                    log_entry = self.format(record)
                    allure.attach(log_entry, name="日志", attachment_type=allure.attachment_type.TEXT)
            
            allure_handler = AllureLogHandler()
            allure_handler.setLevel(logging.INFO)
            
            for logger in cls._loggers.values():
                logger.addHandler(allure_handler)
                
        except ImportError:
            pass  # Allure未安装时忽略


# 获取默认日志器
def get_logger(name: str = None) -> logging.Logger:
    """获取日志器的便捷函数"""
    return LoggerManager.get_logger(name)


# 日志装饰器
def log_step(step_name: str = None):
    """步骤日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            name = step_name or f"{func.__name__}"
            logger.info(f"开始执行步骤: {name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"步骤执行成功: {name}")
                return result
            except Exception as e:
                logger.error(f"步骤执行失败: {name}, 错误: {e}")
                raise
        return wrapper
    return decorator