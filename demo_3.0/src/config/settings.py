"""配置加载模块"""

import os
import yaml
from pathlib import Path


class Config:
    """系统配置类"""

    def __init__(self, config_file: str = None):
        """
        初始化配置

        Args:
            config_file: 配置文件路径，默认为项目根目录下的config.yaml
        """
        if config_file is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "config.yaml"

        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str):
        """加载YAML配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None):
        """
        获取配置值（支持点号分隔的嵌套键）

        Args:
            key: 配置键，如 "database.host"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def app_name(self):
        """应用名称"""
        return self.get("app.name", "Vehicle Routing Planning System")

    @property
    def app_version(self):
        """应用版本"""
        return self.get("app.version", "1.0.0")

    @property
    def debug(self):
        """调试模式"""
        return self.get("app.debug", True)

    @property
    def host(self):
        """服务器主机"""
        return self.get("app.host", "127.0.0.1")

    @property
    def port(self):
        """服务器端口"""
        return self.get("app.port", 5000)

    @property
    def database_url(self):
        """数据库连接URL"""
        user = self.get("database.user", "root")
        password = self.get("database.password", "")
        host = self.get("database.host", "localhost")
        port = self.get("database.port", 3306)
        database = self.get("database.database", "vrp_project")
        charset = self.get("database.charset", "utf8mb4")

        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"

    @property
    def amap_api_key(self):
        """高德地图API密钥"""
        return self.get("amap.api_key", "")

    @property
    def amap_default_city(self):
        """高德地图默认城市"""
        return self.get("amap.default_city", "湘潭市")

    @property
    def cost_weights(self):
        """成本计算权重"""
        return self.get("cost_weights", {
            "distance": 0.5,
            "congestion": 0.3,
            "construction": 0.2
        })

    @property
    def cache_size(self):
        """缓存大小"""
        return self.get("cache.address_cache_size", 100)

    @property
    def log_level(self):
        """日志级别"""
        return self.get("logging.level", "INFO")

    @property
    def log_file(self):
        """日志文件路径"""
        return self.get("logging.file", "logs/app.log")


# 全局配置实例
_config = None


def get_config() -> Config:
    """
    获取全局配置实例

    Returns:
        Config: 配置实例
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
