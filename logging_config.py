# logging_config.py
import logging
import json
from datetime import datetime
import traceback
from typing import Any, Dict, Optional, Tuple


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "operation": getattr(record, "operation", "unknown"),
            "message": record.getMessage(),
            "path": record.pathname,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra contextual data if present
        if hasattr(record, "data"):
            log_data["data"] = record.data

        return json.dumps(log_data)


def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(CustomFormatter())
    logger.addHandler(file_handler)

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger, service: str):
        super().__init__(logger, {})
        self.service = service

    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        kwargs["extra"] = kwargs.get("extra", {})
        kwargs["extra"]["service"] = self.service
        return msg, kwargs

    def log_operation(self, level: int, operation: str, message: str,
                      data: Optional[Dict[str, Any]] = None, exc_info=None):
        extra = {
            "operation": operation,
            "data": data
        }
        self.log(level, message, extra=extra, exc_info=exc_info)
