#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author         : Charlie Zhang
# @Email          : charlie.zhang2@ibaiqiu.com
# @Time           : 2026/6/3 18:10
# @Version        : 1.0
# @File           : settings.py
# @Software       : PyCharm
# logging configuration
import sys
import logging
import os
from config.conf import load_user_config
from config.logging import InterceptHandler
from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = load_user_config()
DEBUG = CONFIG.DEBUG

MYSQL_HOST = CONFIG.MYSQL_HOST
MYSQL_PORT = CONFIG.MYSQL_PORT
MYSQL_USER = CONFIG.MYSQL_USER
MYSQL_PWD = CONFIG.MYSQL_PWD
MYSQL_DB = CONFIG.MYSQL_DB

# Redis配置
REDIS_HOST = CONFIG.REDIS_HOST
REDIS_PORT = CONFIG.REDIS_PORT
REDIS_PWD = CONFIG.REDIS_PWD
REDIS_DB = CONFIG.REDIS_DB

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

log_file_path = os.path.join(BASE_DIR, 'logs/wise.log')
err_log_file_path = os.path.join(BASE_DIR, 'logs/wise.err.log')
isolation_log_file_path = os.path.join(BASE_DIR, 'logs/isolation.log')  # 一键隔离日志
port_mapping_log_file_path = os.path.join(BASE_DIR, 'logs/port_mapping.log')  # 端口映射日志
interception_log_file_path = os.path.join(BASE_DIR, 'logs/interception.log')  # 风险拦截日志

# 埋点日志格式化
format_buried_logs = "<green>{time:YYYY-mm-dd HH:mm:ss.SSS}</green> <level>{message}</level>"

loguru_config = {
    "handlers": [
        {"sink": sys.stderr, "level": "INFO",
         "format": "<green>{time:YYYY-mm-dd HH:mm:ss.SSS}</green> | {thread.name} | <level>{level}</level> | "
                   "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"},
        {"sink": log_file_path, "rotation": "500 MB", "encoding": 'utf-8'},
        {"sink": err_log_file_path, "serialize": True, "level": 'ERROR', "rotation": "500 MB",
         "encoding": 'utf-8'},
    ],
}
logger.configure(**loguru_config)
