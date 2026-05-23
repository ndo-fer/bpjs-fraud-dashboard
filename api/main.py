"""
FastAPI backend untuk VerifiKlaim — dashboard-figma.
Menyediakan endpoint untuk scoring, claims management,
batches, history, audit log, dan user management.
"""

from __future__ import annotations

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Any

import pandas as pd
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Query
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.database import (
    fetch_audit,
    fetch_batches,
    fetch_claims,
    fetch_claim_by_id,
    fetch_history,
    fetch_users,
    fetch_user_by_email,
    insert_audit,
    insert_batch,
    insert_scoring,
    update_claim_status as db_update_claim_status,
    upsert_claim,
    upsert_user,
)
from utils.schema import USER_INPUT_FEATURES
from utils.scoring import (
    THRESHOLD_HIGH,
    explain_single_claim,
    load_artifacts,
    load_model_metadata,
    score_dataframe,
)
from api.auth_db import save_credentials, get_credentials

app = FastAPI(
    title="VerifiKlaim API",
    description="REST API untuk scoring risiko klaim BPJS dan manajemen verifikasi.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_artifacts = None


def get_artifacts():
    global _artifacts
    if _artifacts is None:
        _artifacts = load_artifacts()
    return _artifacts


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Pydantic Models ────────────────────────────────────────────────

class TopFactor(BaseModel):
    feature: str
    feature_value: Any
    contribution: float
    abs_contribution: float
    direction: str


class ScoreResult(BaseModel):
    risk_score: float
    risk_percent: float
    priority: str
    threshold_used: float | None = None
    model_version: str | None = None
    threshold_reference: str | None = None
    top_factors: list[TopFactor] = []
    explanation_metadata: dict[str, Any] | None = None
    raw_response: dict[str, Any] | None = None
    input: dict[str, Any]


class BatchScoreInput(BaseModel):
    filename: str
    uploaded_by: str = "system"
    claims: list[dict[str, Any]]


class BatchScoreResponse(BaseModel):
    batch_id: str
    total: int
    high: int
    medium: int
    low: int
    results: list[ScoreResult]


class ClaimStatusUpdate(BaseModel):
    status: str
    note: str | None = None
    reviewer: str | None = None


class AuditEventIn(BaseModel):
    actor: str
    actor_role: str
    action: str
    entity: str
    entity_id: str
    detail: str
    category: str


class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    role: str
    org: str

class LoginUser(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    org: str
    status: str
    lastActive: str | None = None


# ── Internal helpers ───────────────────────────────────────────────

def _build_score_row(claim_input: dict[str, Any]) -> dict[str, Any]:
    """Map frontend-friendly fields onto BPJS feature schema defaults."""
    row = {}
    for feat in USER_INPUT_FEATURES:
        row[feat] = claim_input.get(feat)

    # Convenience mappings from frontend simplified fields
    if row.get("tarif_disetujui") is None and claim_input.get("amount"):
        row["tarif_disetujui"] = float(claim_input["amount"])
    if row.get("lama_rawat_hari") is None and claim_input.get("los"):
        row["lama_rawat_hari"] = float(claim_input["los"])

    patient_cat = claim_input.get("patient_category", "")
    if row.get("flag_rawat_inap") is None:
        row["flag_rawat_inap"] = 1 if "inpatient" in patient_cat.lower() else 0

    # Pass-through any remaining keys (diagnosis codes, etc.)
    for k, v in claim_input.items():
        if k in USER_INPUT_FEATURES and row.get(k) is None:
            row[k] = v

    return row


def _score_and_persist(
    claims: list[dict[str, Any]],
    source: str,
    batch_id: str | None = None,
) -> list[dict[str, Any]]:
    """Score a list of claim dicts, persist to Supabase, return enriched records."""
    score_rows = [_build_score_row(c) for c in claims]
    scored_df = score_dataframe(pd.DataFrame(score_rows))

    records: list[dict[str, Any]] = []
    for claim, row in zip(claims, scored_df.to_dict(orient="records")):
        rec = {
            **claim,
            "source": source,
            "batch_id": batch_id,
            "risk_score": round(float(row["risk_score"]), 6),
            "risk_percent": round(float(row["risk_percent"]), 2),
            "priority": _normalize_priority(row["priority"]),
            "threshold_used": round(float(row["threshold_used"]), 4),
            "iforest_score": round(float(row["iforest_score"]), 6),
            "model_domain": row.get("model_domain", "reguler"),
            "created_at": now_iso(),
        }
        records.append(rec)

    try:
        insert_scoring(records)
    except Exception as exc:
        print(f"[WARN] Supabase insert_scoring gagal: {exc}")

    return records


def _normalize_priority(raw: str) -> str:
    """Normalize 'High Priority' → 'High' for frontend consumption."""
    return raw.replace(" Priority", "").strip()


def _build_score_result(row: dict[str, Any], explanation: dict | None = None, metadata: dict | None = None) -> ScoreResult:
    meta = metadata or {}
    top_factors: list[TopFactor] = []
    if explanation:
        for f in explanation.get("top_drivers_up", [])[:3]:
            top_factors.append(TopFactor(**f))
    return ScoreResult(
        risk_score=row["risk_score"],
        risk_percent=row["risk_percent"],
        priority=row["priority"],
        threshold_used=row.get("threshold_used"),
        model_version=meta.get("winner_label", "winner_model"),
        threshold_reference=str(meta.get("threshold", row.get("threshold_used", ""))),
        top_factors=top_factors,
        explanation_metadata={"model_domain": row.get("model_domain")} if not explanation else {
            "base_value": explanation.get("base_value"),
            "top_drivers_up_count": len(explanation.get("top_drivers_up", [])),
            "top_drivers_down_count": len(explanation.get("top_drivers_down", [])),
            "model_domain": row.get("model_domain"),
        },
        raw_response={
            "iforest_score": row.get("iforest_score"),
            "model_domain": row.get("model_domain"),
        },
        input={k: row.get(k) for k in USER_INPUT_FEATURES if row.get(k) is not None},
    )


# ── Health ─────────────────────────────────────────────────────────

@app.get("/health")
def health():
    artifacts = get_artifacts()
    info = artifacts["winner_info"]
    return {
        "status": "ok",
        "model": type(artifacts["clf"]).__name__,
        "domain": info.get("domain", "reguler"),
        "n_features": len(USER_INPUT_FEATURES),
        "winner_threshold": float(info.get("threshold", THRESHOLD_HIGH)),
        "model_version": info.get("winner_label", "winner_model"),
        "threshold_reference": str(info.get("threshold", THRESHOLD_HIGH)),
    }

@app.get("/schema")
def schema():
    from api.database import _get_service_client, TABLE_USERS
    client = _get_service_client()
    res = client.table(TABLE_USERS).select("*").limit(1).execute()
    cols = list(res.data[0].keys()) if res.data else []
    return {"columns": cols, "raw_data": res.data}






# ── Single Claim Scoring ───────────────────────────────────────────

@app.post("/predict", response_model=ScoreResult)
def predict(claim: dict[str, Any]):
    try:
        records = _score_and_persist([claim], source="single")
        row = records[0]
        explanation = explain_single_claim(_build_score_row(claim), top_n=4)
        metadata = load_model_metadata()

        # Also upsert as a claim record
        if claim.get("claim_id"):
            try:
                upsert_claim({
                    "id": claim["claim_id"],
                    "facility": claim.get("facility", ""),
                    "org": claim.get("org", ""),
                    "patient_category": claim.get("patient_category", ""),
                    "claim_type": claim.get("claim_type", ""),
                    "amount": claim.get("amount", claim.get("tarif_disetujui", 0)),
                    "diagnosis_group": claim.get("diagnosis_group", ""),
                    "risk_score": row["risk_score"],
                    "risk_percent": row["risk_percent"],
                    "priority": row["priority"],
                    "status": "Needs Review",
                    "reviewer": "",
                    "batch_id": None,
                    "submitted_at": now_iso(),
                    "updated_at": now_iso(),
                    "top_factors": [f["feature"] for f in explanation.get("top_drivers_up", [])[:3]],
                    "los": claim.get("los", claim.get("lama_rawat_hari", 0)),
                    "source": "single",
                })
            except Exception as exc:
                print(f"[WARN] upsert_claim gagal: {exc}")

        return _build_score_result(row, explanation, metadata)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Batch Scoring ──────────────────────────────────────────────────

@app.post("/batch-score", response_model=BatchScoreResponse)
def batch_score(body: BatchScoreInput):
    if not body.claims:
        raise HTTPException(status_code=400, detail="List klaim tidak boleh kosong.")
    try:
        batch_id = f"BTH-{datetime.now(timezone.utc).strftime('%Y-%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        records = _score_and_persist(body.claims, source="batch", batch_id=batch_id)
        metadata = load_model_metadata()

        high = sum(1 for r in records if r["priority"] == "High")
        medium = sum(1 for r in records if r["priority"] == "Medium")
        low = sum(1 for r in records if r["priority"] == "Low")

        # Persist batch header
        try:
            insert_batch({
                "id": batch_id,
                "filename": body.filename,
                "uploaded_by": body.uploaded_by,
                "uploaded_at": now_iso(),
                "total": len(records),
                "high": high,
                "medium": medium,
                "low": low,
                "status": "Processed",
            })
        except Exception as exc:
            print(f"[WARN] insert_batch gagal: {exc}")

        # Upsert individual claim records
        for r, claim in zip(records, body.claims):
            if claim.get("claim_id"):
                try:
                    upsert_claim({
                        "id": claim["claim_id"],
                        "facility": claim.get("facility", ""),
                        "org": claim.get("org", ""),
                        "patient_category": claim.get("patient_category", ""),
                        "claim_type": claim.get("claim_type", ""),
                        "amount": claim.get("amount", claim.get("tarif_disetujui", 0)),
                        "diagnosis_group": claim.get("diagnosis_group", ""),
                        "risk_score": r["risk_score"],
                        "risk_percent": r["risk_percent"],
                        "priority": r["priority"],
                        "status": "New",
                        "reviewer": "",
                        "batch_id": batch_id,
                        "submitted_at": now_iso(),
                        "updated_at": now_iso(),
                        "top_factors": [],
                        "los": claim.get("los", claim.get("lama_rawat_hari", 0)),
                        "source": "batch",
                    })
                except Exception as exc:
                    print(f"[WARN] upsert_claim (batch) gagal: {exc}")

        results = [_build_score_result(r, metadata=metadata) for r in records]
        return BatchScoreResponse(
            batch_id=batch_id,
            total=len(results),
            high=high,
            medium=medium,
            low=low,
            results=results,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# Legacy endpoint (kept for Streamlit compatibility)
@app.post("/batch-predict")
def batch_predict(claims: list[dict[str, Any]]):
    if not claims:
        raise HTTPException(status_code=400, detail="List klaim tidak boleh kosong.")
    try:
        records = _score_and_persist(claims, source="batch")
        metadata = load_model_metadata()
        results = [_build_score_result(r, metadata=metadata) for r in records]
        return {"total": len(results), "results": [r.model_dump() for r in results]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Claims Management ──────────────────────────────────────────────

@app.get("/claims")
def list_claims(limit: int = Query(200, ge=1, le=1000)):
    try:
        data = fetch_claims(limit=limit)
        return {"total": len(data), "records": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/claims/{claim_id}")
def get_claim(claim_id: str):
    try:
        record = fetch_claim_by_id(claim_id)
        if not record:
            raise HTTPException(status_code=404, detail="Claim tidak ditemukan.")
        return record
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.patch("/claims/{claim_id}/status")
def update_claim_status(claim_id: str, body: ClaimStatusUpdate):
    try:
        db_update_claim_status(claim_id, body.status, body.reviewer, body.note)
        # Log audit event
        try:
            insert_audit({
                "id": str(uuid.uuid4()),
                "actor": body.reviewer or "system",
                "actor_role": "verifier",
                "action": "Review status changed",
                "entity": "Claim",
                "entity_id": claim_id,
                "timestamp": now_iso(),
                "detail": f"Status changed to {body.status}" + (f" — {body.note}" if body.note else ""),
                "category": "review",
            })
        except Exception as exc:
            print(f"[WARN] insert_audit gagal: {exc}")
        return {"success": True, "claim_id": claim_id, "status": body.status}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Batches ────────────────────────────────────────────────────────

@app.get("/batches")
def list_batches(limit: int = Query(50, ge=1, le=200)):
    try:
        data = fetch_batches(limit=limit)
        return {"total": len(data), "records": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Scoring History ────────────────────────────────────────────────

@app.get("/history")
def history(limit: int = Query(200, ge=1, le=1000)):
    try:
        data = fetch_history(limit=limit)
        return {"total": len(data), "records": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Audit Log ──────────────────────────────────────────────────────

@app.get("/audit")
def list_audit(limit: int = Query(200, ge=1, le=1000)):
    try:
        data = fetch_audit(limit=limit)
        return {"total": len(data), "events": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/audit")
def create_audit(body: AuditEventIn):
    try:
        event = {
            "id": str(uuid.uuid4()),
            "actor": body.actor,
            "actor_role": body.actor_role,
            "action": body.action,
            "entity": body.entity,
            "entity_id": body.entity_id,
            "timestamp": now_iso(),
            "detail": body.detail,
            "category": body.category,
        }
        insert_audit(event)
        return event
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Users ──────────────────────────────────────────────────────────

@app.get("/users")
def list_users():
    try:
        data = fetch_users()
        # hide passwords and rename last_active -> lastActive
        records = []
        for r in data:
            r.pop("password_hash", None)
            if "last_active" in r:
                r["lastActive"] = r.pop("last_active")
            records.append(r)
        return {"total": len(records), "records": records}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Auth ───────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/auth/register", response_model=AuthResponse)
def register(body: RegisterUser):
    try:
        existing = fetch_user_by_email(body.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
        
        user_id = f"usr-{str(uuid.uuid4())[:8]}"
        user_record = {
            "id": user_id,
            "name": body.name,
            "email": body.email,
            "role": body.role,
            "org": body.org,
            "status": "Active",
            "lastActive": now_iso(),
        }
        
        # Save password locally to SQLite
        hashed_pw = _hash_password(body.password)
        save_credentials(body.email, hashed_pw)
        
        # Save user info to Supabase without password_hash
        upsert_user(user_record)
        return AuthResponse(**user_record)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/auth/login", response_model=AuthResponse)
def login(body: LoginUser):
    try:
        user = fetch_user_by_email(body.email)
        if not user:
            raise HTTPException(status_code=401, detail="Email atau password salah.")
        
        # Get password hash from local SQLite
        hashed = get_credentials(body.email)
        if not hashed:
            raise HTTPException(status_code=401, detail="Email atau password salah.")
        
        # Check password
        input_hashed = _hash_password(body.password)
        if hashed != input_hashed:
            raise HTTPException(status_code=401, detail="Email atau password salah.")
            
        if user.get("status") == "Inactive":
            raise HTTPException(status_code=403, detail="Akun tidak aktif.")
            
        # Update lastActive
        user["lastActive"] = now_iso()
        user.pop("last_active", None)
        user.pop("password_hash", None)
        upsert_user(user)
        
        return AuthResponse(**user)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
