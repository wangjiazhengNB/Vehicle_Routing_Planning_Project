"""日志工具模块"""

import logging
import os
from pathlib import Path

from colorlog import ColoredFormatter

from ..config.settings import get_config


class Logger:
    """日志工具类"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称，默认为配置中的app_name

        Returns:
            日志记录器实例
        """
        config = get_config()

        if name is None:
            name = config.app_name

        if name in cls._loggers:
            return cls._loggers[name]

        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.log_level))

        # 避免重复添加handler
        if not logger.handlers:
            # 控制台handler（彩色输出）
            console_handler = logging.StreamHandler()
            console_formatter = ColoredFormatter(
                config.get("logging.format", "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # 文件handler
            log_file = config.log_file
            if log_file:
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)

                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器（便捷函数）

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return Logger.get_logger(name)
