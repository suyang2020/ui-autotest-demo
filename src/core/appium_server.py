"""
Appium服务器管理模块
负责Appium服务器的启动、停止和状态检查
"""
import subprocess
import time
import requests
import psutil
import logging
from typing import Optional
from ..config import config

logger = logging.getLogger(__name__)


class AppiumServer:
    """Appium服务器管理类"""
    
    def __init__(self, host: str = 'localhost', port: int = 4723):
        self.host = host
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.server_url = f"http://{host}:{port}"
    
    def start(self, **kwargs) -> bool:
        """启动Appium服务器"""
        if self.is_running():
            logger.info(f"Appium服务器已在运行 {self.server_url}")
            return True
        
        try:
            # 构建启动命令
            cmd = ['appium', '--address', self.host, '--port', str(self.port)]
            
            # 添加额外参数
            if kwargs.get('relaxed_security'):
                cmd.extend(['--relaxed-security'])
            if kwargs.get('log_level'):
                cmd.extend(['--log-level', kwargs['log_level']])
            if kwargs.get('log_file'):
                cmd.extend(['--log', kwargs['log_file']])
            
            # 启动服务器
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            if self._wait_for_server_start():
                logger.info(f"Appium服务器启动成功: {self.server_url}")
                return True
            else:
                logger.error("Appium服务器启动超时")
                self.stop()
                return False
                
        except FileNotFoundError:
            logger.error("未找到Appium命令，请确保已安装Appium")
            return False
        except Exception as e:
            logger.error(f"启动Appium服务器失败: {e}")
            return False
    
    def stop(self):
        """停止Appium服务器"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                logger.info("Appium服务器已停止")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("强制终止Appium服务器")
            except Exception as e:
                logger.error(f"停止Appium服务器失败: {e}")
            finally:
                self.process = None
    
    def restart(self, **kwargs) -> bool:
        """重启Appium服务器"""
        self.stop()
        time.sleep(2)  # 等待端口释放
        return self.start(**kwargs)
    
    def is_running(self) -> bool:
        """检查Appium服务器是否运行"""
        try:
            # Appium 3.0+ 使用新的端点
            response = requests.get(f"{self.server_url}/status", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _wait_for_server_start(self, timeout: int = 30) -> bool:
        """等待服务器启动"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return True
            time.sleep(1)
        return False
    
    def get_server_info(self) -> dict:
        """获取服务器信息"""
        try:
            # Appium 3.0+ 使用新的端点
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return {}
    
    def kill_existing_servers(self):
        """杀死现有的Appium服务器进程"""
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if process.info['name'] and 'appium' in process.info['name'].lower():
                    process.kill()
                    logger.info(f"已终止Appium进程: {process.info['pid']}")
                elif process.info['cmdline']:
                    cmdline = ' '.join(process.info['cmdline'])
                    if 'appium' in cmdline and str(self.port) in cmdline:
                        process.kill()
                        logger.info(f"已终止端口 {self.port} 上的进程: {process.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue


class AppiumServerManager:
    """Appium服务器管理器"""
    
    def __init__(self):
        appium_config = config.get_appium_config()
        server_url = appium_config.get('server_url', 'http://localhost:4723/wd/hub')
        
        # 解析服务器URL
        parts = server_url.replace('http://', '').replace('/wd/hub', '').split(':')
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 4723
        
        self.server = AppiumServer(host, port)
    
    def ensure_server_running(self, **kwargs) -> bool:
        """确保Appium服务器运行"""
        if not self.server.is_running():
            logger.info("Appium服务器未运行，正在启动...")
            return self.server.start(**kwargs)
        return True
    
    def auto_start_server(self, **kwargs) -> bool:
        """自动启动服务器（如果需要）"""
        return self.ensure_server_running(**kwargs)


# 全局服务器管理器实例
appium_server_manager = AppiumServerManager()