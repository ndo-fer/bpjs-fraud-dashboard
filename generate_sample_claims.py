"""
Generate 100 sample klaim yang bervariasi dan divalidasi terhadap model
dashboard-v2 saat ini.

Output:
- data/sample_100_claims_mixed.csv
- data/sample_100_claims_mixed_scored_preview.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils.schema import DEFAULT_INPUT_VALUES, USER_INPUT_FEATURES
from utils.scoring import score_dataframe

RNG = np.random.default_rng(seed=20260520)


def make_low(n: int) -> pd.DataFrame:
    return pd.DataFrame({
        "usia": RNG.integers(18, 46, n),
        "tarif_disetujui": RNG.integers(150_000, 2_500_000, n),
        "lama_rawat_hari": RNG.integers(1, 4, n),
        "severity_level_num": RNG.choice([1, 2], n, p=[0.8, 0.2]),
        "jumlah_diagnosis_sekunder": RNG.integers(0, 3, n),
        "fktp_hist_count_before": RNG.integers(0, 2, n),
        "nonkap_hist_count_before": RNG.integers(0, 2, n),
        "flag_kelas_upgrade": np.zeros(n, dtype=int),
        "flag_status_nonaktif": np.zeros(n, dtype=int),
        "flag_meninggal": np.zeros(n, dtype=int),
        "flag_rawat_inap": np.ones(n, dtype=int),
        "flag_special_cmg": np.zeros(n, dtype=int),
        "total_special_cmg": np.zeros(n, dtype=float),
        "jenis_kelamin": RNG.integers(1, 3, n),
        "hubungan_keluarga": RNG.integers(1, 4, n),
        "kelas_rawat_hak": RNG.choice([1, 2, 3], n, p=[0.2, 0.3, 0.5]),
        "kelas_rawat_klaim": RNG.choice([1, 2, 3], n, p=[0.2, 0.3, 0.5]),
        "segmen_kepesertaan": RNG.integers(1, 4, n),
        "status_kepesertaan": np.ones(n, dtype=int),
        "kepemilikan_fktp": RNG.integers(1, 3, n),
        "jenis_fktp": RNG.integers(1, 3, n),
        "tingkat_layanan": np.full(n, 2),
        "poli_tujuan": RNG.integers(1, 8, n),
        "segmen_peserta_klaim": RNG.integers(1, 5, n),
        "status_pulang": np.ones(n, dtype=int),
        "kepemilikan_faskes": RNG.integers(1, 3, n),
        "jenis_faskes": RNG.integers(1, 4, n),
        "tipe_faskes": RNG.integers(1, 5, n),
        "jenis_pelayanan": np.ones(n, dtype=int),
        "grup_diagnosis_utama": RNG.choice(["RESP", "DIGEST", "INFEKSI", "OBS"], n),
        "kode_diagnosis_utama": RNG.choice(["J18", "A09", "K52", "O80"], n),
        "grup_tindakan_utama": RNG.choice(["NONBEDAH", "MEDIKAL"], n),
        "kode_tindakan_utama": RNG.choice(["99.1", "87.3", "90.5"], n),
        "jenis_inacbg": RNG.integers(1, 4, n),
        "kategori_tindakan": RNG.integers(1, 4, n),
        "regional_tarif_num": RNG.integers(1, 4, n),
        "flag_rujukan_missing": np.zeros(n, dtype=int),
        "tarif_inacbg_dasar": RNG.integers(150_000, 2_300_000, n),
        "tarif_grouping": RNG.integers(200_000, 2_600_000, n),
        "jumlah_special_cmg_aktif": np.zeros(n, dtype=float),
        "jumlah_grup_diagnosis_sekunder": RNG.integers(0, 2, n),
        "nonkap_hist_total_before": RNG.integers(0, 300_000, n),
        "nonkap_hist_mean_before": RNG.integers(0, 200_000, n),
    })


def make_medium(n: int) -> pd.DataFrame:
    return pd.DataFrame({
        "usia": RNG.integers(35, 63, n),
        "tarif_disetujui": RNG.integers(2_000_000, 10_000_000, n),
        "lama_rawat_hari": RNG.integers(3, 10, n),
        "severity_level_num": RNG.choice([2, 3], n, p=[0.7, 0.3]),
        "jumlah_diagnosis_sekunder": RNG.integers(2, 7, n),
        "fktp_hist_count_before": RNG.integers(1, 6, n),
        "nonkap_hist_count_before": RNG.integers(1, 5, n),
        "flag_kelas_upgrade": RNG.choice([0, 1], n, p=[0.6, 0.4]),
        "flag_status_nonaktif": RNG.choice([0, 1], n, p=[0.8, 0.2]),
        "flag_meninggal": np.zeros(n, dtype=int),
        "flag_rawat_inap": np.ones(n, dtype=int),
        "flag_special_cmg": RNG.choice([0, 1], n, p=[0.7, 0.3]),
        "total_special_cmg": RNG.integers(0, 3, n),
        "jenis_kelamin": RNG.integers(1, 3, n),
        "hubungan_keluarga": RNG.integers(1, 5, n),
        "kelas_rawat_hak": RNG.integers(1, 4, n),
        "kelas_rawat_klaim": RNG.integers(1, 4, n),
        "segmen_kepesertaan": RNG.integers(1, 5, n),
        "status_kepesertaan": RNG.choice([1, 2], n, p=[0.8, 0.2]),
        "kepemilikan_fktp": RNG.integers(1, 4, n),
        "jenis_fktp": RNG.integers(1, 4, n),
        "tingkat_layanan": np.full(n, 2),
        "poli_tujuan": RNG.integers(1, 15, n),
        "segmen_peserta_klaim": RNG.integers(1, 6, n),
        "status_pulang": RNG.integers(1, 3, n),
        "kepemilikan_faskes": RNG.integers(1, 4, n),
        "jenis_faskes": RNG.integers(1, 5, n),
        "tipe_faskes": RNG.integers(1, 5, n),
        "jenis_pelayanan": RNG.integers(1, 3, n),
        "grup_diagnosis_utama": RNG.choice(["KARDIO", "INFEKSI", "ONKO", "METAB"], n),
        "kode_diagnosis_utama": RNG.choice(["I20", "E11", "A41", "C50"], n),
        "grup_tindakan_utama": RNG.choice(["MEDIKAL", "BEDAH_MINOR", "NONBEDAH"], n),
        "kode_tindakan_utama": RNG.choice(["36.1", "88.7", "45.2", "99.1"], n),
        "jenis_inacbg": RNG.integers(1, 6, n),
        "kategori_tindakan": RNG.integers(1, 5, n),
        "regional_tarif_num": RNG.integers(1, 6, n),
        "flag_rujukan_missing": RNG.choice([0, 1], n, p=[0.8, 0.2]),
        "tarif_inacbg_dasar": RNG.integers(1_500_000, 9_000_000, n),
        "tarif_grouping": RNG.integers(2_000_000, 11_000_000, n),
        "jumlah_special_cmg_aktif": RNG.integers(0, 3, n),
        "jumlah_grup_diagnosis_sekunder": RNG.integers(1, 4, n),
        "nonkap_hist_total_before": RNG.integers(200_000, 5_000_000, n),
        "nonkap_hist_mean_before": RNG.integers(100_000, 1_500_000, n),
    })


def make_high(n: int) -> pd.DataFrame:
    return pd.DataFrame({
        "usia": RNG.integers(50, 81, n),
        "tarif_disetujui": RNG.integers(8_000_000, 40_000_000, n),
        "lama_rawat_hari": RNG.integers(7, 30, n),
        "severity_level_num": RNG.choice([2, 3], n, p=[0.25, 0.75]),
        "jumlah_diagnosis_sekunder": RNG.integers(5, 15, n),
        "fktp_hist_count_before": RNG.integers(4, 16, n),
        "nonkap_hist_count_before": RNG.integers(4, 20, n),
        "flag_kelas_upgrade": np.ones(n, dtype=int),
        "flag_status_nonaktif": RNG.choice([0, 1], n, p=[0.35, 0.65]),
        "flag_meninggal": RNG.choice([0, 1], n, p=[0.7, 0.3]),
        "flag_rawat_inap": np.ones(n, dtype=int),
        "flag_special_cmg": np.ones(n, dtype=int),
        "total_special_cmg": RNG.integers(2, 8, n),
        "jenis_kelamin": RNG.integers(1, 3, n),
        "hubungan_keluarga": RNG.integers(1, 5, n),
        "kelas_rawat_hak": RNG.integers(1, 4, n),
        "kelas_rawat_klaim": RNG.integers(1, 4, n),
        "segmen_kepesertaan": RNG.integers(1, 5, n),
        "status_kepesertaan": RNG.choice([1, 2, 3], n, p=[0.35, 0.45, 0.2]),
        "kepemilikan_fktp": RNG.integers(1, 4, n),
        "jenis_fktp": RNG.integers(1, 4, n),
        "tingkat_layanan": np.full(n, 2),
        "poli_tujuan": RNG.integers(5, 20, n),
        "segmen_peserta_klaim": RNG.integers(1, 7, n),
        "status_pulang": RNG.integers(1, 4, n),
        "kepemilikan_faskes": RNG.integers(1, 4, n),
        "jenis_faskes": RNG.integers(2, 6, n),
        "tipe_faskes": RNG.integers(2, 6, n),
        "jenis_pelayanan": RNG.integers(1, 3, n),
        "grup_diagnosis_utama": RNG.choice(["KARDIO", "ONKO", "NEURO", "KRITIS"], n),
        "kode_diagnosis_utama": RNG.choice(["I21", "C34", "I63", "A41"], n),
        "grup_tindakan_utama": RNG.choice(["BEDAH_MAJOR", "ICU", "INTERVENSI"], n),
        "kode_tindakan_utama": RNG.choice(["36.1", "39.5", "99.1", "88.7"], n),
        "jenis_inacbg": RNG.integers(3, 8, n),
        "kategori_tindakan": RNG.integers(2, 7, n),
        "regional_tarif_num": RNG.integers(2, 7, n),
        "flag_rujukan_missing": RNG.choice([0, 1], n, p=[0.45, 0.55]),
        "tarif_inacbg_dasar": RNG.integers(6_000_000, 32_000_000, n),
        "tarif_grouping": RNG.integers(8_000_000, 45_000_000, n),
        "jumlah_special_cmg_aktif": RNG.integers(1, 6, n),
        "jumlah_grup_diagnosis_sekunder": RNG.integers(3, 8, n),
        "nonkap_hist_total_before": RNG.integers(2_000_000, 20_000_000, n),
        "nonkap_hist_mean_before": RNG.integers(500_000, 4_000_000, n),
    })


def complete_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in USER_INPUT_FEATURES:
        if col not in out.columns:
            out[col] = DEFAULT_INPUT_VALUES.get(col, 0)
    return out[USER_INPUT_FEATURES]


def generate_candidate() -> pd.DataFrame:
    blocks = [
        make_low(36),
        make_medium(34),
        make_high(30),
    ]
    df = pd.concat(blocks, ignore_index=True)
    df = df.sample(frac=1, random_state=int(RNG.integers(0, 1_000_000))).reset_index(drop=True)
    return complete_columns(df)


def main():
    best_df = None
    best_counts = None

    for _ in range(40):
        candidate = generate_candidate()
        scored = score_dataframe(candidate)
        counts = scored["priority"].value_counts().to_dict()
        high = counts.get("High Priority", 0)
        med = counts.get("Medium Priority", 0)
        low = counts.get("Low Priority", 0)

        if high >= 10 and med >= 15 and low >= 15:
            best_df = candidate
            best_counts = counts
            preview = scored.copy()
            break

        if best_counts is None or (
            high + med >= best_counts.get("High Priority", 0) + best_counts.get("Medium Priority", 0)
        ):
            best_df = candidate
            best_counts = counts
            preview = scored.copy()

    out_csv = "data/sample_100_claims_mixed.csv"
    out_preview = "data/sample_100_claims_mixed_scored_preview.csv"

    best_df.to_csv(out_csv, index=False)
    preview.to_csv(out_preview, index=False)

    print(f"Generated {len(best_df)} claims -> {out_csv}")
    print(f"Scored preview saved -> {out_preview}")
    print("Priority distribution:", best_counts)
    print(preview[["risk_score", "risk_percent", "priority"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
