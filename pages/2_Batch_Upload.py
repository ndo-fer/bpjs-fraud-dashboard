import pandas as pd
import plotly.express as px
import streamlit as st

from utils.api_client import _check_api, score_batch
from utils.schema import FEATURE_LABELS, USER_INPUT_FEATURES
from utils.scoring import score_dataframe
from utils.ui import (
    apply_plotly_theme,
    inject_global_styles,
    render_editorial_aside,
    render_metric_strip,
    render_notice,
    render_page_header,
    render_priority_legend,
    render_section_panel,
    render_sidebar_brand,
)

st.set_page_config(page_title="Batch Risk Scoring", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()
render_sidebar_brand(current_page="batch")

render_page_header(
    eyebrow="Operational Flow",
    title="Batch Risk Scoring",
    subtitle="Upload CSV klaim, tinjau distribusi prioritas, lalu unduh hasil scoring untuk mendukung triage dan review operasional.",
    pills=[("Upload CSV", "primary"), ("Review and export", "neutral")],
)

render_notice(
    "warn",
    "Batasan penggunaan",
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final.",
)

api_ok = _check_api()
if api_ok:
    render_notice("success", "Backend terhubung", "Scoring via FastAPI dan log otomatis ke Supabase.")
else:
    render_notice("warn", "Mode offline", "Backend API tidak berjalan. Scoring tetap tersedia dari model lokal, tetapi tidak di-log.")

with open("data/batch_template.csv", "rb") as file_handle:
    st.download_button(
        "Download Template CSV",
        data=file_handle,
        file_name="batch_template.csv",
        mime="text/csv",
    )

render_section_panel(
    kicker="Step 1",
    title="Siapkan batch review",
    body="Gunakan template resmi agar kolom input konsisten. Setelah file diunggah, dashboard akan merangkum distribusi prioritas dan menyiapkan hasil untuk diunduh kembali.",
    soft=True,
)
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

upload_col, guidance_col = st.columns([1.3, 0.7], gap="large")

with upload_col:
    st.markdown(
        """
        <div class="upload-surface">
          <div class="upload-surface__title">Upload file CSV</div>
          <div class="upload-surface__body">Pastikan struktur kolom mengikuti template. File yang rapi akan mempercepat preview, scoring, dan export hasil akhir.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Pilih file CSV klaim", type=["csv"])

with guidance_col:
    render_editorial_aside(
        title="Checklist cepat",
        body="Halaman ini dirancang sebagai meja review operasional. Begitu file masuk, fokus utamanya adalah membaca ringkasan distribusi, lalu menyaring klaim yang paling layak diperiksa terlebih dahulu.",
        items=[
            ("Gunakan template", "Cara paling aman untuk menghindari mismatch kolom adalah mulai dari template yang disediakan."),
            ("Mulai dari summary", "Baca dulu total, high, medium, dan low priority sebelum turun ke tabel rinci."),
            ("Filter lalu ekspor", "Pakai filter prioritas untuk membuat daftar kerja yang lebih fokus sebelum diunduh."),
        ],
    )
    render_priority_legend()

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    with upload_col:
        with st.expander("Preview data (5 baris pertama)"):
            st.dataframe(df.head().rename(columns=FEATURE_LABELS), width="stretch")

    missing_cols = [column for column in USER_INPUT_FEATURES if column not in df.columns]
    if missing_cols:
        readable_missing = [FEATURE_LABELS.get(column, column) for column in missing_cols]
        render_notice(
            "danger",
            "Format CSV tidak sesuai",
            "Kolom yang belum ada: "
            + ", ".join(readable_missing)
            + ". Gunakan template CSV di atas lalu sesuaikan struktur file.",
        )
    else:
        if api_ok:
            records = df[USER_INPUT_FEATURES].to_dict(orient="records")
            api_results = score_batch(records)
            result = df.copy()
            result["risk_score"] = [row["risk_score"] for row in api_results]
            result["risk_percent"] = [row["risk_percent"] for row in api_results]
            result["priority"] = [row["priority"] for row in api_results]
            result = result.sort_values("risk_score", ascending=False).reset_index(drop=True)
        else:
            result = score_dataframe(df)

        total = len(result)
        high_count = (result["priority"] == "High Priority").sum()
        medium_count = (result["priority"] == "Medium Priority").sum()
        low_count = (result["priority"] == "Low Priority").sum()
        average_risk = result["risk_percent"].mean()

        render_section_panel(
            kicker="Step 2",
            title="Baca ringkasan batch",
            body="Mulai dari distribusi prioritas untuk memahami komposisi batch, lalu gunakan tabel hasil untuk menyusun daftar tindak lanjut.",
        )

        render_metric_strip(
            [
                {"label": "Total Klaim", "value": str(total), "note": "klaim diproses", "strong": True},
                {"label": "High Priority", "value": str(high_count), "note": f"{high_count / total:.0%} dari total"},
                {"label": "Medium Priority", "value": str(medium_count), "note": f"{medium_count / total:.0%} dari total"},
                {"label": "Low Priority", "value": str(low_count), "note": f"{low_count / total:.0%} dari total"},
                {"label": "Rata-rata Risiko", "value": f"{average_risk:.1f}%", "note": "skor probabilitas"},
            ]
        )

        priority_order = ["High Priority", "Medium Priority", "Low Priority"]
        priority_colors = {
            "High Priority": "#a14c4f",
            "Medium Priority": "#b88a3b",
            "Low Priority": "#3d7768",
        }
        counts = result["priority"].value_counts().reindex(priority_order, fill_value=0).reset_index()
        counts.columns = ["Prioritas", "Jumlah"]
        fig = px.bar(
            counts,
            x="Prioritas",
            y="Jumlah",
            text="Jumlah",
            color="Prioritas",
            color_discrete_map=priority_colors,
            title="Distribusi Prioritas Verifikasi",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=56, b=0),
        )
        apply_plotly_theme(fig, horizontal_grid=True, vertical_grid=False)
        st.plotly_chart(fig, width="stretch")
        st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)
        render_section_panel(
            kicker="Step 3",
            title="Tabel hasil scoring",
            body="Gunakan filter untuk memusatkan perhatian pada prioritas tertentu. Kolom skor ditempatkan di depan agar scan visual tetap cepat.",
            soft=True,
        )

        filter_col, info_col = st.columns([2.2, 5.8], gap="large")
        with filter_col:
            filter_priority = st.selectbox(
                "Filter Prioritas",
                ["Semua", "High Priority", "Medium Priority", "Low Priority"],
            )
        with info_col:
            st.caption(
                "Tabel diurutkan menurun berdasarkan risk score agar klaim dengan sinyal terkuat otomatis muncul lebih dahulu."
            )

        output_cols = ["priority", "risk_percent", "risk_score"]
        other_cols = [column for column in result.columns if column not in output_cols]
        display_df = result[output_cols + other_cols].copy()

        if filter_priority != "Semua":
            display_df = display_df[display_df["priority"] == filter_priority]

        st.caption(f"Menampilkan {len(display_df)} dari {total} klaim.")
        st.dataframe(display_df.rename(columns=FEATURE_LABELS), width="stretch")

        csv_export = display_df if filter_priority != "Semua" else result[output_cols + other_cols]
        st.download_button(
            "Download Hasil CSV",
            data=csv_export.to_csv(index=False).encode("utf-8"),
            file_name="hasil_scoring.csv",
            mime="text/csv",
        )
else:
    render_notice("info", "Belum ada file", "Upload CSV klaim di atas untuk memulai scoring dan melihat ringkasan batch.")
