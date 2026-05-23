"""
api/database.py
---------------
Supabase client dan helper functions untuk semua tabel VerifiKlaim.

Tabel:
  - scoring_history   (raw ML scoring logs)
  - claims            (claim records dengan status review)
  - batches           (batch upload records)
  - audit_events      (audit trail)
  - app_users         (user management)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from supabase import create_client, Client

load_dotenv(Path(__file__).parent.parent / ".env")

SUPABASE_URL     = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON    = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE = os.getenv("SUPABASE_SERVICE_KEY", "")

TABLE_SCORING  = "scoring_history"
TABLE_CLAIMS   = "claims"
TABLE_BATCHES  = "batch_uploads"   # nama dari dashboard-web schema
TABLE_AUDIT    = "audit_events"
TABLE_USERS    = "app_users"

_service_client: Client | None = None
_anon_client:    Client | None = None


def _get_service_client() -> Client:
    """Client dengan service_role key — bypass RLS, untuk mutasi server-side."""
    global _service_client
    if _service_client is None:
        key = SUPABASE_SERVICE or SUPABASE_ANON
        if not SUPABASE_URL or not key:
            raise RuntimeError("SUPABASE_URL dan SUPABASE_SERVICE_KEY harus diisi di .env")
        _service_client = create_client(SUPABASE_URL, key)
    return _service_client


def _get_anon_client() -> Client:
    """Client dengan anon key — untuk SELECT (dikontrol RLS)."""
    global _anon_client
    if _anon_client is None:
        if not SUPABASE_URL or not SUPABASE_ANON:
            raise RuntimeError("SUPABASE_URL dan SUPABASE_ANON_KEY harus diisi di .env")
        _anon_client = create_client(SUPABASE_URL, SUPABASE_ANON)
    return _anon_client


# ── scoring_history ────────────────────────────────────────────────

def insert_scoring(records: list[dict[str, Any]]) -> None:
    client = _get_service_client()
    client.table(TABLE_SCORING).insert(records).execute()


def fetch_history(limit: int = 200) -> list[dict[str, Any]]:
    client = _get_service_client()
    response = (
        client.table(TABLE_SCORING)
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


# ── claims ─────────────────────────────────────────────────────────

def upsert_claim(record: dict[str, Any]) -> None:
    client = _get_service_client()
    mapped = {
        "claim_code":         record.get("id"),
        "facility_name_text": record.get("facility"),
        "org_name_text":      record.get("org"),
        "patient_category":   record.get("patient_category"),
        "claim_type":         record.get("claim_type"),
        "amount":             record.get("amount"),
        "diagnosis_group":    record.get("diagnosis_group"),
        "risk_score":         record.get("risk_score"),
        "risk_percent":       record.get("risk_percent"),
        "priority":           record.get("priority"),
        "status":             record.get("status"),
        "reviewer":           record.get("reviewer"),
        "batch_id":           record.get("batch_id"),
        "submitted_at":       record.get("submitted_at"),
        "updated_at":         record.get("updated_at"),
        "top_factors":        record.get("top_factors"),
        "length_of_stay":     int(record.get("los") or 0),
        "source":             record.get("source"),
    }
    # Cari existing UUID id by claim_code
    try:
        existing = client.table(TABLE_CLAIMS).select("id").eq("claim_code", record.get("id")).limit(1).execute()
        if existing.data:
            mapped["id"] = existing.data[0]["id"]
    except Exception as e:
        print(f"[WARN] Gagal query existing claim UUID: {e}")
        
    client.table(TABLE_CLAIMS).upsert(mapped, on_conflict="claim_code").execute()


def fetch_claims(limit: int = 200) -> list[dict[str, Any]]:
    client = _get_service_client()
    response = (
        client.table(TABLE_CLAIMS)
        .select("*")
        .order("submitted_at", desc=True)
        .limit(limit)
        .execute()
    )
    # Normalize ke format frontend
    results = []
    for r in response.data:
        results.append({
            "id":              r.get("claim_code") or str(r.get("id", "")),
            "facility":        r.get("facility_name_text") or str(r.get("facility_id") or ""),
            "org":             r.get("org_name_text") or str(r.get("organization_id") or ""),
            "patientCategory": r.get("patient_category", ""),
            "claimType":       r.get("claim_type", ""),
            "amount":          float(r.get("amount") or 0),
            "diagnosisGroup":  r.get("diagnosis_group", ""),
            "riskScore":       float(r.get("risk_score") or 0),
            "riskPercent":     float(r.get("risk_percent") or 0),
            "priority":        r.get("priority", "Low"),
            "status":          r.get("status", "New"),
            "reviewer":        r.get("reviewer", ""),
            "batchId":         r.get("batch_id"),
            "submittedAt":     r.get("submitted_at") or r.get("created_at", ""),
            "updatedAt":       r.get("updated_at") or r.get("created_at", ""),
            "topFactors":      r.get("top_factors") or [],
            "los":             float(r.get("length_of_stay") or r.get("los") or 0),
            "source":          r.get("source", "single"),
        })
    return results


def fetch_claim_by_id(claim_id: str) -> dict[str, Any] | None:
    """Cari claim by claim_code (TEXT) atau uuid id."""
    client = _get_service_client()
    # Coba cari by claim_code dulu
    response = (
        client.table(TABLE_CLAIMS)
        .select("*")
        .eq("claim_code", claim_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        # Fallback ke UUID id
        response = (
            client.table(TABLE_CLAIMS)
            .select("*")
            .eq("id", claim_id)
            .limit(1)
            .execute()
        )
    if not response.data:
        return None
    r = response.data[0]
    return {
        "id":              r.get("claim_code") or str(r.get("id", "")),
        "facility":        r.get("facility_name_text") or str(r.get("facility_id") or ""),
        "org":             r.get("org_name_text") or str(r.get("organization_id") or ""),
        "patientCategory": r.get("patient_category", ""),
        "claimType":       r.get("claim_type", ""),
        "amount":          float(r.get("amount") or 0),
        "diagnosisGroup":  r.get("diagnosis_group", ""),
        "riskScore":       float(r.get("risk_score") or 0),
        "riskPercent":     float(r.get("risk_percent") or 0),
        "priority":        r.get("priority", "Low"),
        "status":          r.get("status", "New"),
        "reviewer":        r.get("reviewer", ""),
        "batchId":         r.get("batch_id"),
        "submittedAt":     r.get("submitted_at") or r.get("created_at", ""),
        "updatedAt":       r.get("updated_at") or r.get("created_at", ""),
        "topFactors":      r.get("top_factors") or [],
        "los":             float(r.get("length_of_stay") or r.get("los") or 0),
        "source":          r.get("source", "single"),
    }


def update_claim_status(
    claim_id: str,
    status: str,
    reviewer: str | None = None,
    note: str | None = None,
) -> None:
    from datetime import datetime, timezone
    client = _get_service_client()
    update: dict[str, Any] = {
        "status":     status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if reviewer:
        update["reviewer"] = reviewer
    if note:
        update["last_note"] = note
    # Coba update by claim_code dulu
    res = client.table(TABLE_CLAIMS).update(update).eq("claim_code", claim_id).execute()
    if not res.data:
        # Fallback ke UUID
        client.table(TABLE_CLAIMS).update(update).eq("id", claim_id).execute()


# ── batches ────────────────────────────────────────────────────────

def insert_batch(record: dict[str, Any]) -> None:
    """Insert batch upload record — mapping ke schema batch_uploads."""
    client = _get_service_client()
    # Map field names ke schema batch_uploads
    mapped = {
        "batch_code":  record.get("id", ""),
        "filename":    record.get("filename", ""),
        "total_rows":  record.get("total", 0),
        "status":      record.get("status", "pending").lower(),
        "high":        record.get("high", 0),
        "medium":      record.get("medium", 0),
        "low":         record.get("low", 0),
        "created_at":  record.get("uploaded_at"),
        "processed_at": record.get("uploaded_at"),
    }
    client.table(TABLE_BATCHES).insert(mapped).execute()


def fetch_batches(limit: int = 50) -> list[dict[str, Any]]:
    client = _get_service_client()
    response = (
        client.table(TABLE_BATCHES)
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    # Normalize ke format yang diharapkan frontend
    results = []
    for r in response.data:
        results.append({
            "id":         r.get("batch_code") or str(r.get("id", "")),
            "filename":   r.get("filename", ""),
            "uploadedBy": str(r.get("uploaded_by") or "system"),
            "uploadedAt": r.get("created_at", ""),
            "total":      r.get("total_rows", 0),
            "high":       r.get("high", 0),
            "medium":     r.get("medium", 0),
            "low":        r.get("low", 0),
            "status":     (r.get("status") or "pending").capitalize(),
        })
    return results


# ── audit_events ───────────────────────────────────────────────────

def insert_audit(event: dict[str, Any]) -> None:
    """Insert audit event — mapping ke schema audit_events."""
    client = _get_service_client()
    # audit_events schema: actor_name, actor_role, action, entity_type, entity_id, detail (jsonb)
    mapped = {
        "actor_name":   event.get("actor", ""),
        "actor_role":   event.get("actor_role", ""),
        "action":       event.get("action", ""),
        "entity_type":  event.get("entity", ""),
        "entity_id":    event.get("entity_id", ""),
        "category":     event.get("category", "claim"),
        "detail":       {"note": event.get("detail", "")},
        "created_at":   event.get("timestamp"),
    }
    client.table(TABLE_AUDIT).insert(mapped).execute()


def fetch_audit(limit: int = 200) -> list[dict[str, Any]]:
    client = _get_service_client()
    response = (
        client.table(TABLE_AUDIT)
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    # Normalize ke format yang diharapkan frontend
    results = []
    for r in response.data:
        detail = r.get("detail") or {}
        results.append({
            "id":        str(r.get("id", "")),
            "actor":     r.get("actor_name") or r.get("actor_name_text", "System"),
            "actor_role": r.get("actor_role", ""),
            "action":    r.get("action", ""),
            "entity":    r.get("entity_type", ""),
            "entity_id": r.get("entity_id", ""),
            "timestamp": r.get("created_at", ""),
            "detail":    detail.get("note", "") if isinstance(detail, dict) else str(detail),
            "category":  r.get("category", "claim"),
        })
    return results


# ── app_users ──────────────────────────────────────────────────────

def fetch_users() -> list[dict[str, Any]]:
    client = _get_service_client()
    response = (
        client.table(TABLE_USERS)
        .select("*")
        .order("name")
        .execute()
    )
    return response.data


def upsert_user(user: dict[str, Any]) -> None:
    client = _get_service_client()
    client.table(TABLE_USERS).upsert(user, on_conflict="id").execute()
