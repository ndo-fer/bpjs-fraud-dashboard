"""
inspect_model.py
----------------
Skrip diagnostik untuk memverifikasi bahwa model dapat di-load
dan menerima input dengan fitur yang benar.

Jalankan dari folder dashboard-v2:
    python inspect_model.py
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path("models/winner_model.joblib")
REF_STATS_PATH = Path("models/reference_stats.json")


def main():
    print("=" * 60)
    print("INSPEKSI MODEL")
    print("=" * 60)

    # 1. Load model
    print(f"\n[1] Loading model dari: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print("  ERROR: File tidak ditemukan!")
        sys.exit(1)

    model = joblib.load(MODEL_PATH)
    print(f"  ✓ Model berhasil dimuat")
    print(f"  Tipe : {type(model).__name__}")

    # 2. Feature names
    if hasattr(model, "feature_names_in_"):
        features = list(model.feature_names_in_)
        print(f"\n[2] Fitur yang dibutuhkan model ({len(features)} fitur):")
        for i, f in enumerate(features, 1):
            print(f"  {i:2d}. {f}")
    else:
        print("\n[2] Model tidak memiliki feature_names_in_ (sklearn < 1.0)")
        features = []

    # 3. Load reference_stats.json
    print(f"\n[3] Loading reference_stats dari: {REF_STATS_PATH}")
    if not REF_STATS_PATH.exists():
        print("  WARNING: reference_stats.json tidak ditemukan")
    else:
        with open(REF_STATS_PATH, "r", encoding="utf-8") as f:
            ref = json.load(f)
        schema_features = ref.get("all_model_features", [])
        print(f"  ✓ Loaded. Schema features: {len(schema_features)}")

        # Cek konsistensi
        if features:
            model_set = set(features)
            schema_set = set(schema_features)
            missing_in_schema = model_set - schema_set
            missing_in_model = schema_set - model_set
            if missing_in_schema:
                print(f"  ⚠ Fitur di model tapi tidak di schema: {missing_in_schema}")
            if missing_in_model:
                print(f"  ⚠ Fitur di schema tapi tidak di model: {missing_in_model}")
            if not missing_in_schema and not missing_in_model:
                print("  ✓ Schema dan model konsisten!")

    # 4. Test inference dengan dummy data
    print("\n[4] Test inference dengan dummy data (10 input features)...")

    try:
        from utils.scoring import build_full_feature_df, score_dataframe

        dummy = pd.DataFrame([{
            "usia": 45,
            "severity_level": 2,
            "lama_rawat_hari": 5,
            "tarif_disetujui": 5_000_000,
            "total_special_cmg": 1,
            "jumlah_diagnosis_sekunder": 3,
            "flag_status_nonaktif": 0,
            "flag_kelas_upgrade": 0,
            "fktp_hist_count_before": 2,
            "nonkap_hist_count_before": 1,
        }])

        X_full = build_full_feature_df(dummy)
        print(f"  Input shape  : {dummy.shape}")
        print(f"  Full X shape : {X_full.shape}")
        print(f"  Kolom X      : {list(X_full.columns)}")

        scores = model.predict_proba(X_full)[:, 1]
        print(f"\n  ✓ Scoring berhasil!")
        print(f"  Risk score   : {scores[0]:.4f} ({scores[0]*100:.2f}%)")
        print(f"  Priority     : {'High' if scores[0] >= 0.8 else 'Medium' if scores[0] >= 0.4 else 'Low'}")

    except Exception as e:
        print(f"  ERROR saat inference: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
