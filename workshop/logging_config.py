import os
import json
from datetime import datetime

class RedactFilter:
    """Oculta valores de claves sensibles en mensajes/extra."""
    SENSITIVE_KEYS = {"password", "token", "secret", "authorization", "passwd", "api_key"}

    def filter(self, record):
        try:
            if isinstance(record.msg, dict):
                record.msg = self._redact_dict(record.msg)
            if hasattr(record, "__dict__"):
                for k in list(record.__dict__.keys()):
                    if k.lower() in self.SENSITIVE_KEYS:
                        record.__dict__[k] = "***REDACTED***"
        except Exception:
            pass
        return True

    def _redact_dict(self, d):
        def _walk(obj):
            if isinstance(obj, dict):
                return {k: ("***REDACTED***" if k.lower() in self.SENSITIVE_KEYS else _walk(v)) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_walk(x) for x in obj]
            return obj
        return _walk(d)

class JsonFormatter:
    def format(self, record):
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = True
        return json.dumps(payload, ensure_ascii=False)

LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "redact": {"()": RedactFilter},
    },
    "formatters": {
        "json": {"()": JsonFormatter},
        "console": {"format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "filters": ["redact"],
            "formatter": "console",
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "filters": ["redact"],
            "formatter": "json",
            "filename": os.environ.get("DJANGO_LOG_FILE", "logs/app.jsonl"),
            "maxBytes": int(os.environ.get("DJANGO_LOG_MAX_BYTES", "10485760")),  # 10 MB
            "backupCount": int(os.environ.get("DJANGO_LOG_BACKUP_COUNT", "5")),
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console", "json_file"],
    },
}
