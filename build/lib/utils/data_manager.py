"""
测试数据管理模块
提供测试数据的读取、生成和管理功能
"""
import json
import yaml
import csv
import random
import string
from pathlib import Path
from typing import Dict, List, Any, Union, Optional
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, data_dir: str = "src/tests/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._data_cache = {}
    
    def load_json_data(self, filename: str) -> Dict[str, Any]:
        """加载JSON测试数据"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning(f"JSON数据文件不存在: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"加载JSON数据成功: {filepath}")
            return data
        except Exception as e:
            logger.error(f"加载JSON数据失败: {e}")
            return {}
    
    def load_yaml_data(self, filename: str) -> Dict[str, Any]:
        """加载YAML测试数据"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning(f"YAML数据文件不存在: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            logger.debug(f"加载YAML数据成功: {filepath}")
            return data
        except Exception as e:
            logger.error(f"加载YAML数据失败: {e}")
            return {}
    
    def load_csv_data(self, filename: str) -> List[Dict[str, str]]:
        """加载CSV测试数据"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning(f"CSV数据文件不存在: {filepath}")
            return []
        
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            logger.debug(f"加载CSV数据成功: {filepath}, 共 {len(data)} 条记录")
            return data
        except Exception as e:
            logger.error(f"加载CSV数据失败: {e}")
            return []
    
    def get_data(self, filename: str, key: str = None) -> Any:
        """获取测试数据"""
        # 检查缓存
        if filename in self._data_cache:
            data = self._data_cache[filename]
        else:
            # 根据文件扩展名选择加载方法
            file_path = self.data_dir / filename
            if file_path.suffix.lower() == '.json':
                data = self.load_json_data(filename)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                data = self.load_yaml_data(filename)
            elif file_path.suffix.lower() == '.csv':
                data = self.load_csv_data(filename)
            else:
                logger.error(f"不支持的数据文件格式: {filename}")
                return None
            
            # 缓存数据
            self._data_cache[filename] = data
        
        # 返回指定键的数据或全部数据
        if key and isinstance(data, dict):
            return data.get(key)
        return data
    
    def save_json_data(self, filename: str, data: Dict[str, Any]):
        """保存JSON测试数据"""
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存JSON数据成功: {filepath}")
        except Exception as e:
            logger.error(f"保存JSON数据失败: {e}")
    
    def clear_cache(self):
        """清空数据缓存"""
        self._data_cache.clear()
        logger.debug("已清空数据缓存")


class DataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def random_string(length: int = 8, chars: str = None) -> str:
        """生成随机字符串"""
        chars = chars or string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def random_number(min_val: int = 1, max_val: int = 100) -> int:
        """生成随机数字"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_email(domain: str = "example.com") -> str:
        """生成随机邮箱"""
        username = DataGenerator.random_string(8).lower()
        return f"{username}@{domain}"
    
    @staticmethod
    def random_phone(prefix: str = "13") -> str:
        """生成随机手机号"""
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        return f"{prefix}{suffix}"
    
    @staticmethod
    def random_chinese_name() -> str:
        """生成随机中文姓名"""
        surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "涛"]
        
        surname = random.choice(surnames)
        name = ''.join(random.choices(names, k=random.randint(1, 2)))
        return f"{surname}{name}"
    
    @staticmethod
    def random_date(start_date: str = None, end_date: str = None, format: str = "%Y-%m-%d") -> str:
        """生成随机日期"""
        if start_date:
            start = datetime.strptime(start_date, format)
        else:
            start = datetime.now() - timedelta(days=365)
        
        if end_date:
            end = datetime.strptime(end_date, format)
        else:
            end = datetime.now()
        
        random_date = start + timedelta(days=random.randint(0, (end - start).days))
        return random_date.strftime(format)
    
    @staticmethod
    def random_id_card() -> str:
        """生成随机身份证号（仅用于测试）"""
        # 地区码
        area_codes = ["110101", "310115", "440106", "440301"]
        area_code = random.choice(area_codes)
        
        # 出生日期
        birth_date = DataGenerator.random_date("1970-01-01", "2000-12-31", "%Y%m%d")
        
        # 顺序码
        sequence = str(random.randint(100, 999))
        
        # 校验码计算（简化版）
        check_codes = "10X98765432"
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        
        id_17 = area_code + birth_date + sequence
        sum_val = sum(int(id_17[i]) * weights[i] for i in range(17))
        check_code = check_codes[sum_val % 11]
        
        return id_17 + check_code


class UserDataFactory:
    """用户数据工厂"""
    
    @staticmethod
    def create_user_data(user_type: str = "normal") -> Dict[str, str]:
        """创建用户数据"""
        base_data = {
            "username": DataGenerator.random_string(8),
            "password": "Test123456",
            "email": DataGenerator.random_email(),
            "phone": DataGenerator.random_phone(),
            "name": DataGenerator.random_chinese_name(),
            "id_card": DataGenerator.random_id_card()
        }
        
        if user_type == "admin":
            base_data["username"] = f"admin_{DataGenerator.random_string(6)}"
            base_data["role"] = "admin"
        elif user_type == "vip":
            base_data["username"] = f"vip_{DataGenerator.random_string(6)}"
            base_data["level"] = "vip"
        
        return base_data
    
    @staticmethod
    def create_login_data() -> List[Dict[str, str]]:
        """创建登录测试数据"""
        return [
            {"username": "valid_user", "password": "valid_password", "expected": "success"},
            {"username": "invalid_user", "password": "valid_password", "expected": "fail"},
            {"username": "valid_user", "password": "invalid_password", "expected": "fail"},
            {"username": "", "password": "valid_password", "expected": "fail"},
            {"username": "valid_user", "password": "", "expected": "fail"},
        ]


# 全局实例
test_data_manager = TestDataManager()
data_generator = DataGenerator()
user_data_factory = UserDataFactory()


# 便捷函数
def get_test_data(filename: str, key: str = None) -> Any:
    """获取测试数据的便捷函数"""
    return test_data_manager.get_data(filename, key)


def generate_user_data(user_type: str = "normal") -> Dict[str, str]:
    """生成用户数据的便捷函数"""
    return user_data_factory.create_user_data(user_type)