"""
utils/api_client.py
--------------------
HTTP client untuk Streamlit → FastAPI communication.

Streamlit tidak lagi load model langsung — semua scoring
dilakukan melalui FastAPI backend di :8000.
"""

from __future__ import annotations

import os
import math
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT  = 30  # detik


def _sanitize_jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if pd.isna(value):
        return None
    return value


def _sanitize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: _sanitize_jsonable(value) for key, value in record.items()}


def _check_api() -> bool:
    """Cek apakah FastAPI backend sedang berjalan."""
    try:
        r = httpx.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def score_single(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    POST /predict — score satu klaim.
    Returns dict dengan risk_score, risk_percent, priority.
    """
    payload = _sanitize_record(input_data)
    r = httpx.post(f"{API_BASE}/predict", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def score_batch(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    POST /batch-predict — score banyak klaim.
    Returns list of result dicts.
    """
    payload = [_sanitize_record(record) for record in records]
    r = httpx.post(f"{API_BASE}/batch-predict", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["results"]


def get_history(limit: int = 200) -> pd.DataFrame:
    """
    GET /history — ambil riwayat scoring dari Supabase via API.
    Returns DataFrame.
    """
    r = httpx.get(f"{API_BASE}/history", params={"limit": limit}, timeout=TIMEOUT)
    r.raise_for_status()
    records = r.json().get("records", [])
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)
