"""
Skrip diagnostik untuk memverifikasi artifact multidomain/reguler
yang dipakai oleh dashboard-v2.
"""

from __future__ import annotations

import traceback

import pandas as pd

from utils.scoring import ARTIFACT_DIR, build_full_feature_df, load_artifacts, score_dataframe


def main():
    print("=" * 60)
    print("INSPEKSI ARTIFACT DASHBOARD-V2")
    print("=" * 60)
    print(f"Artifact dir: {ARTIFACT_DIR}")

    artifacts = load_artifacts()
    info = artifacts["winner_info"]

    print(f"Winner model : {info.get('winner_model')}")
    print(f"Domain       : {info.get('domain')}")
    print(f"CV mode      : {info.get('cv_mode')}")
    print(f"Threshold    : {info.get('threshold')}")
    print(f"Winner feats : {len(info.get('winner_features', []))}")

    try:
        dummy = pd.DataFrame([{
            "usia": 45,
            "tarif_disetujui": 5_000_000,
            "lama_rawat_hari": 5,
            "severity_level_num": 2,
            "jumlah_diagnosis_sekunder": 3,
            "fktp_hist_count_before": 2,
            "nonkap_hist_count_before": 1,
            "flag_kelas_upgrade": 0,
            "flag_status_nonaktif": 0,
            "flag_meninggal": 0,
            "flag_rawat_inap": 1,
            "flag_special_cmg": 0,
            "total_special_cmg": 0,
        }])

        full_df = build_full_feature_df(dummy)
        scored = score_dataframe(dummy)

        print(f"Input cols   : {list(dummy.columns)}")
        print(f"Full cols    : {len(full_df.columns)}")
        print(f"Risk score   : {scored.iloc[0]['risk_score']:.4f}")
        print(f"Priority     : {scored.iloc[0]['priority']}")
        print(f"IF score     : {scored.iloc[0]['iforest_score']:.4f}")
    except Exception as exc:
        print(f"ERROR saat test inference: {exc}")
        traceback.print_exc()

    print("=" * 60)


if __name__ == "__main__":
    main()
