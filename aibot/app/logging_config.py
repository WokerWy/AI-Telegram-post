import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from datetime import datetime


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # structured data
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record, ensure_ascii=False)


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # ===== File handler (JSON) =====
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(JsonFormatter())

    # ===== Console handler (readable) =====
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)
