import streamlit as st
import pandas as pd
import plotly.express as px

from utils.scoring import score_dataframe, THRESHOLD_HIGH, THRESHOLD_MEDIUM
from utils.schema import USER_INPUT_FEATURES, FEATURE_LABELS

st.set_page_config(
    page_title="Batch Upload",
    layout="wide"
)

st.title("Batch Risk Scoring")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

# ── Download template ──────────────────────────────────────────────────────────
with open("data/batch_template.csv", "rb") as file:
    st.download_button(
        label="⬇ Download Template CSV",
        data=file,
        file_name="batch_template.csv",
        mime="text/csv"
    )

# ── Upload file ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload CSV klaim", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Preview Data")
    st.dataframe(df.head().rename(columns=FEATURE_LABELS))

    missing_cols = [col for col in USER_INPUT_FEATURES if col not in df.columns]

    if missing_cols:
        readable_missing = [FEATURE_LABELS.get(col, col) for col in missing_cols]
        st.error("Format CSV belum sesuai.")
        st.write("Kolom yang belum ada:")
        for col in readable_missing:
            st.markdown(f"- {col}")
        st.info("Silakan download template CSV di atas, lalu isi data sesuai format tersebut.")

    else:
        result = score_dataframe(df)

        # ── Ringkasan metrik ───────────────────────────────────────────────────
        st.subheader("Ringkasan Hasil")

        total_claim    = len(result)
        high_priority  = (result["priority"] == "High Priority").sum()
        medium_priority = (result["priority"] == "Medium Priority").sum()
        low_priority   = (result["priority"] == "Low Priority").sum()
        avg_risk       = result["risk_percent"].mean().round(2)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Klaim",     total_claim)
        col2.metric("🔴 High Priority",  high_priority)
        col3.metric("🟡 Medium Priority", medium_priority)
        col4.metric("🟢 Low Priority",   low_priority)
        col5.metric("Rata-rata Risiko", f"{avg_risk}%")

        # ── Bar chart distribusi ───────────────────────────────────────────────
        priority_order = ["High Priority", "Medium Priority", "Low Priority"]
        priority_colors = {
            "High Priority":   "#c0392b",
            "Medium Priority": "#d68910",
            "Low Priority":    "#1e8449",
        }

        priority_counts = (
            result["priority"]
            .value_counts()
            .reindex(priority_order, fill_value=0)
            .reset_index()
        )
        priority_counts.columns = ["Prioritas", "Jumlah"]

        fig = px.bar(
            priority_counts,
            x="Prioritas",
            y="Jumlah",
            text="Jumlah",
            color="Prioritas",
            color_discrete_map=priority_colors,
            title="Distribusi Prioritas Verifikasi",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # ── Filter + tabel hasil ───────────────────────────────────────────────
        st.subheader("Hasil Risk Scoring")

        filter_col, _ = st.columns([2, 6])
        with filter_col:
            filter_priority = st.selectbox(
                "Filter Prioritas",
                ["Semua", "High Priority", "Medium Priority", "Low Priority"],
                index=0,
            )

        output_cols = ["priority", "risk_percent", "risk_score"]
        other_cols  = [col for col in result.columns if col not in output_cols]
        display_df  = result[output_cols + other_cols].copy()

        if filter_priority != "Semua":
            display_df = display_df[display_df["priority"] == filter_priority]

        st.caption(f"Menampilkan {len(display_df)} dari {total_claim} klaim.")
        st.dataframe(display_df.rename(columns=FEATURE_LABELS))

        # ── Download hasil ─────────────────────────────────────────────────────
        csv_export = (
            display_df if filter_priority != "Semua" else result[output_cols + other_cols]
        )

        st.download_button(
            label="⬇ Download Hasil CSV",
            data=csv_export.to_csv(index=False).encode("utf-8"),
            file_name="hasil_scoring.csv",
            mime="text/csv",
        )

else:
    st.info("Upload file CSV untuk mulai scoring.")
