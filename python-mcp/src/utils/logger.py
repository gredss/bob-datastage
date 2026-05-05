"""
Simple logging utility
"""

import sys
import json
from datetime import datetime
from typing import Any, Optional
from ..config.constants import ENV


class Logger:
    """Simple logger for DataStage MCP Server"""
    
    def __init__(self):
        self.level = ENV.LOG_LEVEL.lower()
        self.levels = ['debug', 'info', 'warn', 'error']
    
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on current log level"""
        try:
            current_level_index = self.levels.index(self.level)
            message_level_index = self.levels.index(level)
            return message_level_index >= current_level_index
        except ValueError:
            return True
    
    def _format_message(self, level: str, message: str, meta: Optional[Any] = None) -> str:
        """Format log message with timestamp and metadata"""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        meta_str = f' {json.dumps(meta)}' if meta else ''
        return f'[{timestamp}] [{level.upper()}] {message}{meta_str}'
    
    def debug(self, message: str, meta: Optional[Any] = None) -> None:
        """Log debug message"""
        if self._should_log('debug'):
            print(self._format_message('debug', message, meta), file=sys.stderr)
    
    def info(self, message: str, meta: Optional[Any] = None) -> None:
        """Log info message"""
        if self._should_log('info'):
            print(self._format_message('info', message, meta), file=sys.stderr)
    
    def warn(self, message: str, meta: Optional[Any] = None) -> None:
        """Log warning message"""
        if self._should_log('warn'):
            print(self._format_message('warn', message, meta), file=sys.stderr)
    
    def error(self, message: str, meta: Optional[Any] = None) -> None:
        """Log error message"""
        if self._should_log('error'):
            print(self._format_message('error', message, meta), file=sys.stderr)


# Global logger instance
logger = Logger()


# Made with Bob