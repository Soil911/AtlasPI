"""Logging strutturato per AtlasPI."""

import json
import logging
import sys
from contextvars import ContextVar

from src.config import LOG_FORMAT, LOG_LEVEL

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    """Formatter JSON per log di produzione."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get("-"),
        }
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Formatter leggibile per sviluppo locale."""

    def format(self, record: logging.LogRecord) -> str:
        rid = request_id_var.get("-")
        prefix = f"[{rid[:8]}] " if rid != "-" else ""
        return f"{self.formatTime(record)} {record.levelname:<7} {prefix}{record.name}: {record.getMessage()}"


def setup_logging():
    """Configura il logging per tutta l'applicazione."""
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    # Rimuovi handler esistenti
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if LOG_FORMAT == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(TextFormatter())

    root.addHandler(handler)

    # Riduci il rumore di librerie esterne
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
