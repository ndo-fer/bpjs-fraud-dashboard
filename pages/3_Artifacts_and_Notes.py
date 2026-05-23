import pandas as pd
import plotly.express as px
import streamlit as st

from utils.schema import FEATURE_LABELS, USER_INPUT_FEATURES
from utils.scoring import THRESHOLD_HIGH, THRESHOLD_MEDIUM, load_model, load_model_metadata
from utils.ui import (
    apply_plotly_theme,
    inject_global_styles,
    render_metric_strip,
    render_notice,
    render_page_header,
    render_section_panel,
    render_sidebar_brand,
)

st.set_page_config(page_title="Artifacts & Notes", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()
render_sidebar_brand(current_page="artifacts")

metadata = load_model_metadata()
model = load_model()
domain_name = metadata.get("domain", "reguler")
cv_mode = metadata.get("cv_mode", "unknown")
n_folds = metadata.get("n_cv_folds", "-")
winner_model_name = metadata.get("winner_model", type(model).__name__)

render_page_header(
    eyebrow="Model Trust Center",
    title="Artifacts and Notes",
    subtitle="Ringkasan artifact model aktif, metrik evaluasi yang tersimpan, dan catatan interpretasi untuk penggunaan dashboard.",
    pills=[
        (winner_model_name, "primary"),
        (f"{domain_name} domain", "neutral"),
        (f"{cv_mode} CV", "warn"),
    ],
)

render_section_panel(
    kicker="Artifact Summary",
    title="Model aktif di dashboard",
    body="Halaman ini membaca metadata dari artifact multidomain yang sekarang dipakai dashboard, supaya dokumentasi dan scoring tetap konsisten.",
)

holdout_f1 = metadata.get("holdout_f1")
cv_mean_f1 = metadata.get("cv_mean_f1")
threshold = float(metadata.get("threshold", THRESHOLD_HIGH))

metric_items = [
    {"label": "Winner Model", "value": str(winner_model_name), "note": "model terpilih dari pipeline", "strong": True},
    {"label": "CV Mode", "value": str(cv_mode), "note": f"{n_folds} folds" if n_folds != "-" else "cross-validation mode"},
    {"label": "Threshold", "value": f"{threshold:.2f}", "note": "binary threshold artifact"},
]
if cv_mean_f1 is not None:
    metric_items.append({"label": "CV Mean F1", "value": f"{float(cv_mean_f1):.4f}", "note": "rerata validasi silang"})
if holdout_f1 is not None:
    metric_items.append({"label": "Holdout F1", "value": f"{float(holdout_f1):.4f}", "note": "generalization check"})

render_metric_strip(metric_items)
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

render_section_panel(
    kicker="Feature Space",
    title="Feature importance global",
    body="Importance di bawah ini menampilkan sinyal global dari model aktif. Ini berguna untuk orientasi, tetapi bukan penjelasan kausal penuh untuk satu klaim tertentu.",
    soft=True,
)

if hasattr(model, "feature_importances_"):
    raw_importances = list(model.feature_importances_)
    feature_names = list(getattr(model, "feature_names_in_", []))

    if not feature_names:
        feature_names = list(metadata.get("winner_features", []))
    if not feature_names:
        feature_names = USER_INPUT_FEATURES

    pairs = list(zip(feature_names, raw_importances))
    if pairs:
        imp_df = pd.DataFrame(
            {
                "Fitur": [FEATURE_LABELS.get(name, name) for name, _ in pairs],
                "Kode": [name for name, _ in pairs],
                "Importance": [importance for _, importance in pairs],
            }
        ).sort_values("Importance", ascending=False)

        chart_df = imp_df.head(12).sort_values("Importance", ascending=True)

        fig = px.bar(
            chart_df,
            x="Importance",
            y="Fitur",
            orientation="h",
            text=chart_df["Importance"].apply(lambda value: f"{value:.1%}"),
            color_discrete_sequence=["#78b8bf"],
            title="Top feature importance",
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(
            showlegend=False,
            xaxis_title="Importance score",
            yaxis_title="",
            height=max(360, 34 * len(chart_df)),
        )
        apply_plotly_theme(fig, horizontal_grid=True, vertical_grid=False)
        st.plotly_chart(fig, width="stretch")

        top_rows = imp_df.head(5)
        st.markdown("**Fitur paling dominan:**")
        for index, row in enumerate(top_rows.itertuples(), 1):
            st.markdown(f"- **{index}. {row.Fitur}** (`{row.Kode}`) - {row.Importance:.1%}")
    else:
        render_notice("warn", "Importance tidak tersedia", "Model aktif tidak menyediakan pasangan feature name dan importance yang konsisten untuk ditampilkan.")
else:
    render_notice("warn", "Importance tidak tersedia", "Model aktif tidak menyediakan `feature_importances_` untuk divisualisasikan.")

render_section_panel(
    kicker="Thresholding",
    title="Band prioritas dashboard",
    body=f"Artifact menyimpan threshold utama di {threshold:.2f}. Dashboard menambahkan band medium di {THRESHOLD_MEDIUM:.2f} agar hasil lebih mudah dipakai untuk triage harian.",
)
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

threshold_col, note_col = st.columns([1.05, 0.95], gap="large")
with threshold_col:
    threshold_df = pd.DataFrame(
        [
            {"Prioritas": "High Priority", "Kondisi": f"skor >= {THRESHOLD_HIGH:.2f}"},
            {"Prioritas": "Medium Priority", "Kondisi": f"{THRESHOLD_MEDIUM:.2f} <= skor < {THRESHOLD_HIGH:.2f}"},
            {"Prioritas": "Low Priority", "Kondisi": f"skor < {THRESHOLD_MEDIUM:.2f}"},
        ]
    )
    st.dataframe(threshold_df, width="stretch", hide_index=True)
with note_col:
    render_notice(
        "info",
        "Cara baca threshold",
        "Threshold artifact dipakai sebagai batas high priority. Band medium ditambahkan di dashboard untuk membantu prioritas operasional yang lebih bertahap.",
    )

render_section_panel(
    kicker="Input Contract",
    title="Feature input dari dashboard",
    body="Daftar ini menunjukkan field yang diharapkan dari workflow dashboard saat ini. Label tampilan dan nama kode disandingkan agar lebih mudah dicocokkan saat debugging batch input.",
    soft=True,
)

input_rows = pd.DataFrame(
    [{"Label": FEATURE_LABELS.get(feature, feature), "Kode": feature} for feature in USER_INPUT_FEATURES]
)
st.dataframe(input_rows, width="stretch", hide_index=True)

render_notice(
    "danger",
    "Catatan interpretasi",
    "Artifact ini lebih kuat daripada model demo sederhana, tetapi tetap bukan jaminan bebas overfitting. Hasil digunakan untuk membantu prioritas verifikasi internal, bukan keputusan fraud final.",
)
