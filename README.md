# Dashboard Prioritas Verifikasi Klaim

Prototype dashboard untuk membantu prioritas verifikasi klaim menggunakan model machine learning.

## Fitur

- Overview dashboard
- Single Claim Scoring
- Batch Upload CSV
- Risk Scoring
- Priority Classification
- Download hasil scoring
- Artifacts & Notes

## Cara Menjalankan

`powershell
cd F:\ProyekPA\dashboard-v2
.\.venv\Scripts\activate
streamlit run app.py
Model

Model yang digunakan:

models/winner_model.joblib
Input Features
Riwayat Kunjungan FKTP
Upgrade Kelas
Status Kepesertaan Nonaktif
Jumlah Diagnosis Sekunder
Lama Rawat (Hari)
Riwayat Non-Kapitasi
Severity Level
Tarif Disetujui
Total Special CMG
Usia
Disclaimer

Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final.
