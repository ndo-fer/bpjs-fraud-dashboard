import streamlit as st

from utils.ui import (
    inject_global_styles,
    render_metric_strip,
    render_notice,
    render_page_header,
    render_sidebar_brand,
)

st.set_page_config(
    page_title="Overview",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
render_sidebar_brand(current_page="overview")

render_page_header(
    eyebrow="Workspace Overview",
    title="Dashboard overview",
    subtitle="Ringkasan cepat tentang apa yang bisa dilakukan dashboard ini, bagaimana memulainya, dan bagaimana membaca hasilnya dengan tepat.",
    pills=[
        ("Decision-support only", "warn"),
        ("Readable for sidang/demo", "primary"),
    ],
)

render_metric_strip([
    {"label": "Primary Use", "value": "Triage", "note": "Membantu urutan verifikasi klaim, bukan keputusan fraud final.", "strong": True},
    {"label": "Model Scope", "value": "Reguler", "note": "Artifact pemenang domain reguler hasil cross-validation."},
    {"label": "Main Workflows", "value": "3", "note": "Scoring manual, review batch, dan pembacaan evidence model."},
])
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="capability-grid">
      <div class="capability-card">
        <div class="capability-card__eyebrow">Input</div>
        <div class="capability-card__title">Single Claim Scoring</div>
        <div class="capability-card__body">Asesmen satu klaim dengan form inti yang ringan, hasil prioritas yang cepat dibaca, dan ringkasan faktor dominan.</div>
      </div>
      <div class="capability-card">
        <div class="capability-card__eyebrow">Review</div>
        <div class="capability-card__title">Batch Upload</div>
        <div class="capability-card__body">Workflow operasional untuk unggah CSV, membaca distribusi prioritas, dan menelusuri hasil secara cepat.</div>
      </div>
      <div class="capability-card">
        <div class="capability-card__eyebrow">Trust</div>
        <div class="capability-card__title">Artifacts & Notes</div>
        <div class="capability-card__body">Pusat evidensi model: threshold, metrik evaluasi, feature importance, dan caveat yang perlu diketahui.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_notice(
    "info",
    "Cara mulai paling cepat",
    "Gunakan Single Claim Scoring bila ingin menilai satu klaim secara manual. Gunakan Batch Upload bila ingin melihat pola prioritas pada banyak klaim sekaligus.",
)
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.15, 0.85], gap="large")

with col_left:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">Bagaimana membaca output</div>
          <div class="section-copy">
            Dashboard ini menyajikan skor risiko dan prioritas verifikasi. 
            Fokus utama bukan menyimpulkan fraud, melainkan membantu memutuskan klaim mana yang lebih layak diperiksa lebih dulu.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-card section-card--soft">
          <div class="section-title">Urutan penggunaan yang disarankan</div>
          <div class="section-copy">
            1. Buka Single Claim atau Batch Upload sesuai kebutuhan.<br>
            2. Baca prioritas, skor, dan faktor dominan.<br>
            3. Gunakan Artifacts &amp; Notes untuk memahami batasan model.<br>
            4. Cek History bila ingin melihat rekam scoring yang sudah tersimpan.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    render_notice(
        "warn",
        "Framing yang harus dijaga",
        "Semua hasil di dashboard ini adalah indikasi risiko untuk prioritas verifikasi. Tetap gunakan pembacaan manual dan konteks operasional sebelum menarik kesimpulan.",
    )

    render_notice(
        "success",
        "Kekuatan dashboard",
        "Alur kerja sekarang menyatukan input, review batch, dan evidensi model dalam satu workspace yang lebih rapi dan mudah dipresentasikan.",
    )
