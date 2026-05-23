import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ui import (
    apply_plotly_theme,
    inject_global_styles,
    render_sidebar_brand,
    render_page_header,
    render_notice,
    render_metric_strip,
    render_section_intro,
)
from utils.schema import FEATURE_LABELS
from utils.api_client import get_history, _check_api

st.set_page_config(page_title="Scoring History", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()
render_sidebar_brand(current_page="history")

render_page_header(
    eyebrow="Audit Trail",
    title="Scoring History",
    subtitle="Riwayat seluruh klaim yang pernah di-score, tersimpan di Supabase sebagai jejak operasional.",
    pills=[("Supabase", "success"), ("Real-time log", "primary")],
)

# ── Cek API ───────────────────────────────────────────────────────────────────
if not _check_api():
    render_notice(
        "danger",
        "Backend tidak aktif",
        "FastAPI backend tidak berjalan. "
        "Jalankan `uvicorn api.main:app --reload --port 8000` di terminal terpisah.",
    )
    st.stop()

# ── Load history ──────────────────────────────────────────────────────────────
with st.spinner("Mengambil riwayat dari Supabase…"):
    df = get_history(limit=500)

if df.empty:
    render_notice(
        "info",
        "Belum ada riwayat",
        "Lakukan scoring di halaman Single Claim atau Batch Upload terlebih dahulu.",
    )
    st.stop()

# ── Metric strip ──────────────────────────────────────────────────────────────
total   = len(df)
n_high  = (df["priority"] == "High Priority").sum()
n_med   = (df["priority"] == "Medium Priority").sum()
n_low   = (df["priority"] == "Low Priority").sum()

render_metric_strip([
    {"label": "Total Scoring", "value": str(total), "note": "semua sumber", "strong": True},
    {"label": "High Priority", "value": str(n_high), "note": f"{n_high/total:.0%}"},
    {"label": "Medium Priority", "value": str(n_med), "note": f"{n_med/total:.0%}"},
    {"label": "Low Priority", "value": str(n_low), "note": f"{n_low/total:.0%}"},
])

# ── Charts ────────────────────────────────────────────────────────────────────
col_chart, col_src = st.columns(2)

with col_chart:
    priority_order  = ["High Priority", "Medium Priority", "Low Priority"]
    priority_colors = {"High Priority": "#a14c4f", "Medium Priority": "#b88a3b", "Low Priority": "#3d7768"}
    counts = (
        df["priority"].value_counts()
        .reindex(priority_order, fill_value=0)
        .reset_index()
    )
    counts.columns = ["Prioritas", "Jumlah"]
    fig = px.bar(
        counts, x="Prioritas", y="Jumlah", text="Jumlah",
        color="Prioritas", color_discrete_map=priority_colors,
        title="Distribusi Prioritas (All Time)",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
    )
    apply_plotly_theme(fig, horizontal_grid=True, vertical_grid=False)
    st.plotly_chart(fig, width="stretch")

with col_src:
    if "source" in df.columns:
        src_counts = df["source"].value_counts().reset_index()
        src_counts.columns = ["Sumber", "Jumlah"]
        fig2 = px.pie(
            src_counts, names="Sumber", values="Jumlah",
            title="Sumber Scoring",
            color_discrete_sequence=["#1c6a78", "#7a9181"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#31424d", size=14),
            title=dict(font=dict(color="#22313b", size=20), x=0, xanchor="left"),
            legend=dict(font=dict(color="#56636d")),
        )
        fig2.update_traces(textfont=dict(color="#31424d"))
        st.plotly_chart(fig2, width="stretch")

# ── Filter + tabel ────────────────────────────────────────────────────────────
render_section_intro(
    "Riwayat Detail",
    "Filter dan telusuri semua klaim yang pernah di-score.",
    soft=True,
)

col_f1, col_f2, _ = st.columns([2, 2, 4])
with col_f1:
    filter_priority = st.selectbox(
        "Filter Prioritas",
        ["Semua", "High Priority", "Medium Priority", "Low Priority"],
    )
with col_f2:
    if "source" in df.columns:
        filter_source = st.selectbox("Filter Sumber", ["Semua", "single", "batch"])
    else:
        filter_source = "Semua"

display_df = df.copy()
if filter_priority != "Semua":
    display_df = display_df[display_df["priority"] == filter_priority]
if filter_source != "Semua" and "source" in display_df.columns:
    display_df = display_df[display_df["source"] == filter_source]

show_cols = ["created_at", "source", "priority", "risk_percent", "risk_score"] + [
    c for c in display_df.columns
    if c in FEATURE_LABELS and c not in ["risk_score", "risk_percent", "priority"]
]
show_cols = [c for c in show_cols if c in display_df.columns]

st.caption(f"Menampilkan {len(display_df)} dari {total} record.")
st.dataframe(
    display_df[show_cols].rename(columns={
        **FEATURE_LABELS, "created_at": "Waktu", "source": "Sumber",
    }),
    width="stretch",
)

st.download_button(
    "Download Riwayat CSV",
    data=display_df[show_cols].to_csv(index=False).encode("utf-8"),
    file_name="scoring_history.csv", mime="text/csv",
)
