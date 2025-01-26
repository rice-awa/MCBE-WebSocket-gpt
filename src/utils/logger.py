import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

class Logger:
    _logger = None
    _loggers = {}

    @classmethod
    def setup(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger('MinecraftGPT')
            cls._logger.setLevel(logging.DEBUG)

            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            
            # 文件处理器
            file_handler = logging.FileHandler(
                f'logs/minecraft_gpt_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            cls._logger.addHandler(console_handler)
            cls._logger.addHandler(file_handler)

    @classmethod
    def get_logger(cls, name: str, filename: str) -> logging.Logger:
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)

            # 确保日志目录存在
            os.makedirs('logs', exist_ok=True)
            
            # 文件处理器
            file_handler = RotatingFileHandler(
                f'logs/{filename}',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            cls._loggers[name] = logger
            
        return cls._loggers[name]

    @classmethod
    def debug(cls, message):
        cls.setup()
        cls._logger.debug(message)

    @classmethod
    def info(cls, message):
        cls.setup()
        cls._logger.info(message)

    @classmethod
    def warning(cls, message):
        cls.setup()
        cls._logger.warning(message)

    @classmethod
    def error(cls, message):
        cls.setup()
        cls._logger.error(message)

    @classmethod
    def log_game_info(cls, message: str):
        logger = cls.get_logger('game_info', 'game_info.log')
        logger.info(message)

    @classmethod
    def log_player_move(cls, message: str):
        logger = cls.get_logger('player_move', 'player_move.log')
        logger.info(message) 
    
    @classmethod
    def log_player_move_silent(cls, message: str):
        """静默记录玩家移动信息，只写入文件不打印到控制台"""
        logger = cls.get_logger('player_move', 'player_move.log')
        if logging.DEBUG >= logger.getEffectiveLevel():
            logger.debug(message) 