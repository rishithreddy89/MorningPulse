"""Centralized logging utility with color-coded output."""

import sys
from datetime import datetime
from typing import Any


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class Logger:
    """Simple logger with color-coded output."""
    
    @staticmethod
    def _timestamp() -> str:
        """Get current timestamp."""
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def _print(color: str, prefix: str, message: str) -> None:
        """Print colored log message."""
        timestamp = Logger._timestamp()
        print(f"{color}[{timestamp}] {prefix}{Colors.RESET} {message}", flush=True)
    
    @staticmethod
    def info(message: str) -> None:
        """Log info message (green)."""
        Logger._print(Colors.GREEN, "✓", message)
    
    @staticmethod
    def error(message: str) -> None:
        """Log error message (red)."""
        Logger._print(Colors.RED, "✗ ERROR", message)
    
    @staticmethod
    def warning(message: str) -> None:
        """Log warning message (yellow)."""
        Logger._print(Colors.YELLOW, "⚠ WARN", message)
    
    @staticmethod
    def step(step_name: str) -> None:
        """Log pipeline step (blue, bold)."""
        timestamp = Logger._timestamp()
        print(f"{Colors.BLUE}{Colors.BOLD}[{timestamp}] ▶ {step_name}{Colors.RESET}", flush=True)
    
    @staticmethod
    def request(method: str, path: str) -> None:
        """Log HTTP request (cyan)."""
        Logger._print(Colors.CYAN, "REQ", f"{method} {path}")
    
    @staticmethod
    def success(message: str) -> None:
        """Log success message (green, bold)."""
        timestamp = Logger._timestamp()
        print(f"{Colors.GREEN}{Colors.BOLD}[{timestamp}] ✓ {message}{Colors.RESET}", flush=True)
    
    @staticmethod
    def data(label: str, value: Any) -> None:
        """Log data point (magenta)."""
        Logger._print(Colors.MAGENTA, "DATA", f"{label}: {value}")


# Convenience functions
def log_info(message: str) -> None:
    """Log info message."""
    Logger.info(message)


def log_error(message: str) -> None:
    """Log error message."""
    Logger.error(message)


def log_warning(message: str) -> None:
    """Log warning message."""
    Logger.warning(message)


def log_step(step_name: str) -> None:
    """Log pipeline step."""
    Logger.step(step_name)


def log_request(method: str, path: str) -> None:
    """Log HTTP request."""
    Logger.request(method, path)


def log_success(message: str) -> None:
    """Log success message."""
    Logger.success(message)


def log_data(label: str, value: Any) -> None:
    """Log data point."""
    Logger.data(label, value)
