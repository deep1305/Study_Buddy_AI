from __future__ import annotations

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# You can override with an environment variable if needed.
LOGS_DIR = Path(os.getenv("LOGS_DIR", "logs"))

_configured = False


def configure_logging(
    *,
    level: int = logging.INFO,
    log_dir: Path = LOGS_DIR,
    fmt: str = DEFAULT_LOG_FORMAT,
) -> None:
    """
    Configure root logging once (file + console).

    Why:
    - Avoids calling logging.basicConfig() at import-time (library-friendly)
    - Avoids duplicate handlers when imported multiple times
    """
    global _configured
    if _configured:
        return

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    formatter = logging.Formatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)

    # Add a daily rotating file handler (keeps 7 days).
    if not any(
        isinstance(h, TimedRotatingFileHandler)
        and getattr(h, "baseFilename", None) == str(log_file)
        for h in root.handlers
    ):
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    # Add console output for local dev / containers.
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger; ensures logging is configured at least once.
    """
    configure_logging()
    return logging.getLogger(name)