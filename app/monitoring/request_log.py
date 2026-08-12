from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from app.config import settings

def log_analysis_event(event: dict) -> None:
    if not settings.request_logging_enabled:
        return

    os.makedirs(os.path.dirname(settings.request_log_path), exist_ok=True)

    payload = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    **event,
    }

    with open(settings.request_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")