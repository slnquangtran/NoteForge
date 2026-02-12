"""
NoteForge Logger Module
Provides cross-platform logging functionality.
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = 'noteforge', level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting across platforms.
    
    Args:
        name: Logger name (default: 'noteforge')
        level: Logging level (default: logging.INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (will be prefixed with 'noteforge.')
    
    Returns:
        Logger instance
    """
    if not name.startswith('noteforge.'):
        name = f'noteforge.{name}'
    return logging.getLogger(name)
