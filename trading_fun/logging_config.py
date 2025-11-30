"""
Structured logging configuration with request tracking and performance metrics.
"""
import logging
import sys
import time
from contextvars import ContextVar
from typing import Optional
from uuid import uuid4

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class RequestIdFilter(logging.Filter):
    """Add request ID to log records."""
    
    def filter(self, record):
        record.request_id = request_id_var.get() or "no-request"
        return True


class StructuredFormatter(logging.Formatter):
    """
    JSON-like structured logging formatter.
    Format: [timestamp] [level] [request_id] message {extra_fields}
    """
    
    def format(self, record):
        # Base format
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = record.levelname
        request_id = getattr(record, 'request_id', 'no-request')
        message = record.getMessage()
        
        # Build log line
        log_line = f"[{timestamp}] [{level:8s}] [{request_id[:8]}] {message}"
        
        # Add extra fields if present
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'stack_info', 'thread', 'threadName', 'request_id', 'exc_info', 'exc_text']:
                extra_fields[key] = value
        
        if extra_fields:
            import json
            log_line += f" {json.dumps(extra_fields, default=str)}"
        
        # Add exception info if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line


def setup_logging(log_level: str = "INFO"):
    """Configure structured logging for the application."""
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Add formatter and filter
    console_handler.setFormatter(StructuredFormatter())
    console_handler.addFilter(RequestIdFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger


class RequestLogger:
    """Context manager for request logging with timing."""
    
    def __init__(self, endpoint: str, **kwargs):
        self.endpoint = endpoint
        self.extra = kwargs
        self.start_time = None
        self.request_id = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        # Generate request ID
        self.request_id = str(uuid4())
        request_id_var.set(self.request_id)
        
        # Log request start
        self.start_time = time.time()
        self.logger.info(
            f"Request started: {self.endpoint}",
            extra={"endpoint": self.endpoint, "event": "request_start", **self.extra}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Calculate duration
        duration_ms = (time.time() - self.start_time) * 1000
        
        # Log request end
        if exc_type:
            self.logger.error(
                f"Request failed: {self.endpoint}",
                extra={
                    "endpoint": self.endpoint,
                    "event": "request_error",
                    "duration_ms": round(duration_ms, 2),
                    "error": str(exc_val),
                    **self.extra
                },
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            self.logger.info(
                f"Request completed: {self.endpoint}",
                extra={
                    "endpoint": self.endpoint,
                    "event": "request_complete",
                    "duration_ms": round(duration_ms, 2),
                    **self.extra
                }
            )
        
        # Clear request ID
        request_id_var.set(None)
    
    def log_metric(self, metric_name: str, value: float, **kwargs):
        """Log a metric during request processing."""
        self.logger.info(
            f"Metric: {metric_name}",
            extra={
                "endpoint": self.endpoint,
                "event": "metric",
                "metric_name": metric_name,
                "metric_value": value,
                **kwargs,
                **self.extra
            }
        )
