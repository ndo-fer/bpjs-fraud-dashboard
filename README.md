# Dashboard Prioritas Verifikasi Klaim

Prototype dashboard decision-support untuk prioritas verifikasi klaim menggunakan model machine learning XGBoost.

## Cara Menjalankan

```powershell
cd F:\ProyekPA\dashboard-v2
.\.venv\Scripts\activate
streamlit run app.py
```

Akses di browser: http://localhost:8501

## Fitur Dashboard

| Halaman | Fitur |
|---|---|
| **Overview** | Penjelasan dashboard dan navigasi |
| **Single Claim Scoring** | Input manual satu klaim, hasil skor risiko + top 3 faktor dominan |
| **Batch Upload** | Upload CSV banyak klaim, filter prioritas, download hasil |
| **Artifacts & Notes** | Feature importance chart, metrik model, threshold, disclaimer |

## Model

- **File**: `models/winner_model.joblib`
- **Algoritma**: XGBoost Classifier
- **Fitur**: 10 fitur utama (lihat di bawah)
- **ROC-AUC**: 0.9999 | **F1-Score**: 0.9525

## Input Features (10 Fitur)

| Fitur | Keterangan |
|---|---|
| `usia` | Usia peserta |
| `severity_level` | Tingkat keparahan (1-3) |
| `lama_rawat_hari` | Lama rawat inap (hari) |
| `tarif_disetujui` | Tarif klaim yang disetujui |
| `total_special_cmg` | Total special CMG |
| `jumlah_diagnosis_sekunder` | Jumlah diagnosis sekunder |
| `flag_status_nonaktif` | Status kepesertaan nonaktif (0/1) |
| `flag_kelas_upgrade` | Upgrade kelas rawat (0/1) |
| `fktp_hist_count_before` | Riwayat kunjungan FKTP sebelumnya |
| `nonkap_hist_count_before` | Riwayat klaim non-kapitasi sebelumnya |

## Format CSV untuk Batch Upload

Download template dari halaman **Batch Upload**, atau buat CSV dengan 10 kolom di atas.

## Disclaimer

> Output model adalah **indikasi risiko untuk prioritas verifikasi**, bukan keputusan fraud final.
> Dashboard ini merupakan prototype akademik berbasis pseudo-label.
