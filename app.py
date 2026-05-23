import streamlit as st

from utils.ui import (
    inject_global_styles,
    render_metric_strip,
    render_page_header,
    render_sidebar_brand,
)

st.set_page_config(
    page_title="Dashboard PA",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
render_sidebar_brand(current_page="home")

render_page_header(
    eyebrow="Editorial Console",
    title="Claim Review Studio",
    subtitle="Workspace untuk prioritas verifikasi klaim dengan alur input, review batch, dan evidensi model yang lebih terarah.",
    pills=[
        ("Artifact reguler aktif", "success"),
        ("Prototype akademik", "primary"),
    ],
)

render_metric_strip([
    {"label": "Use This App For", "value": "Single", "note": "Scoring satu klaim dengan hasil yang cepat dibaca.", "strong": True},
    {"label": "Operational Flow", "value": "Batch", "note": "Upload, ringkas, dan review distribusi prioritas."},
    {"label": "Model Trust", "value": "Evidence", "note": "Lihat threshold, metrik, dan feature importance."},
])
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="capability-grid">
      <div class="capability-card">
        <div class="capability-card__eyebrow">Overview</div>
        <div class="capability-card__title">Orientasi cepat</div>
        <div class="capability-card__body">Mulai dari overview untuk memahami model aktif, alur kerja dashboard, dan konteks penggunaan yang aman.</div>
      </div>
      <div class="capability-card">
        <div class="capability-card__eyebrow">Single Claim</div>
        <div class="capability-card__title">Guided scoring</div>
        <div class="capability-card__body">Gunakan input inti untuk asesmen cepat dan membaca hasil prioritas verifikasi dengan format yang lebih terarah.</div>
      </div>
      <div class="capability-card">
        <div class="capability-card__eyebrow">Batch Upload</div>
        <div class="capability-card__title">Review desk</div>
        <div class="capability-card__body">Unggah CSV, baca distribusi prioritas, lalu telusuri klaim hasil scoring dengan ritme kerja yang lebih rapi.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <div class="section-title">Cara pakai singkat</div>
      <div class="section-copy">
        Buka halaman yang sesuai dari sidebar. Mulai dari <strong>Single Claim Scoring</strong> untuk asesmen manual, 
        atau <strong>Batch Upload</strong> untuk review banyak klaim sekaligus. 
        Setelah itu gunakan <strong>Artifacts &amp; Notes</strong> untuk membaca konteks model dan <strong>History</strong> untuk melihat jejak scoring yang sudah tersimpan.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
