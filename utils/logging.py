"""
Project-wide logging configuration.

This module provides a single, centralized logger for the entire application.
Logs are written to both console and a log file.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from os.path import exists, join
from time import time

from flask import request

from wms_server.settings import Config

if not exists(Config.LOG_DIR):
    os.makedirs(Config.LOG_DIR)


# Configure the root logger
def configure_logging(log_level=logging.INFO):
    """Configure the root logger with file and console handlers.

    Args:
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the root logger level
    root_logger.setLevel(log_level)

    # Create formatters
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation (10MB per file, keep 5 backups)
    log_file = join(Config.LOG_DIR, "wms_service.log")
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


# Initialize the logger
configure_logging()

# Create a module-level logger instance
logger = logging.getLogger(__name__)


def request_logger_decorator(func):
    def wrapper(*args, **kwargs):
        logger.info(
            f"Request Method: {request.method}, Request URL: {request.url}, Request Args: {request.args}"
        )
        start_time = time()
        ret = func(*args, **kwargs)
        logger.info(f"Response Status Code: {ret}")
        exe_time = round(time() - start_time, 2)
        logger.info(f"Request took {exe_time} seconds")
        return ret

    return wrapper


def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time()
        function_name = func.__name__
        ret = func(*args, **kwargs)
        exe_time = round(time() - start_time, 2)
        logger.info(f"{function_name} executed in {exe_time} seconds")
        return ret

    return wrapper
