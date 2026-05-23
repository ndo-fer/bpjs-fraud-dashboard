import pandas as pd
import plotly.express as px
import streamlit as st

from utils.api_client import _check_api, score_single
from utils.schema import CORE_INPUT_FEATURES, FEATURE_LABELS, USER_INPUT_FEATURES
from utils.scoring import THRESHOLD_HIGH, THRESHOLD_MEDIUM, explain_single_claim, load_model
from utils.ui import (
    apply_plotly_theme,
    inject_global_styles,
    render_editorial_aside,
    render_metric_strip,
    render_notice,
    render_page_header,
    render_priority_legend,
    render_result_hero,
    render_section_panel,
    render_sidebar_brand,
)

st.set_page_config(page_title="Single Claim Scoring", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()
render_sidebar_brand(current_page="single")

render_page_header(
    eyebrow="Guided Scoring",
    title="Single Claim Scoring",
    subtitle="Masukkan satu klaim untuk menilai prioritas verifikasi, lalu baca hasilnya dalam format yang lebih mudah diinterpretasikan.",
    pills=[("Fast review flow", "primary"), ("Single-claim assessment", "neutral")],
)

render_notice(
    "warn",
    "Batasan penggunaan",
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final. Prediksi berbasis pseudo-label, bukan label fraud terverifikasi.",
)

api_ok = _check_api()
if api_ok:
    render_notice("success", "Backend terhubung", "Scoring via FastAPI dan log otomatis ke Supabase.")
else:
    render_notice("warn", "Mode offline", "Backend API tidak berjalan. Scoring tetap berjalan dari model lokal, tetapi tidak di-log.")

render_section_panel(
    kicker="Step 1",
    title="Susun profil klaim",
    body="Isi input inti yang paling memengaruhi profil klaim. Form ini dijaga tetap ringkas agar nyaman untuk simulasi maupun pengecekan cepat.",
    soft=True,
)
st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

DERIVED_FEATURES = {"beban_histori", "intensitas_diag_sekunder"}
SOURCE_LABELS = {
    "input_user": "Input user",
    "derived": "Turunan input",
    "default_fallback": "Default/fallback",
}


def classify_feature_source(feature_name: str) -> str:
    if feature_name in CORE_INPUT_FEATURES:
        return "input_user"
    if feature_name in DERIVED_FEATURES:
        return "derived"
    return "default_fallback"

input_col, guide_col = st.columns([1.35, 0.85], gap="large")

with input_col:
    st.markdown('<div class="section-kicker">Core Input</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Data Klaim</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Nilai awal disiapkan netral. Kamu bisa pakai halaman ini untuk simulasi ringan atau membaca satu klaim secara manual sebelum masuk ke batch review.</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        fktp_hist_count_before = st.number_input("Riwayat Kunjungan FKTP", min_value=0, value=0)
        flag_kelas_upgrade = st.selectbox(
            "Upgrade Kelas",
            [0, 1],
            format_func=lambda value: "Ya" if value else "Tidak",
        )
        flag_status_nonaktif = st.selectbox(
            "Status Kepesertaan Nonaktif",
            [0, 1],
            format_func=lambda value: "Ya" if value else "Tidak",
        )
        jumlah_diagnosis_sekunder = st.number_input("Jumlah Diagnosis Sekunder", min_value=0, value=0)
        lama_rawat_hari = st.number_input("Lama Rawat (Hari)", min_value=0, value=0)

    with right_col:
        nonkap_hist_count_before = st.number_input("Riwayat Non-Kapitasi", min_value=0, value=0)
        severity_level_num = st.selectbox("Severity Level", [1, 2, 3])
        tarif_disetujui = st.number_input("Tarif Disetujui", min_value=0, value=0, step=100_000)
        total_special_cmg = st.number_input("Total Special CMG", min_value=0, value=0)
        usia = st.number_input("Usia", min_value=0, max_value=120, value=30)

with guide_col:
    render_editorial_aside(
        title="Cara membaca assessment",
        body="Skor dipakai untuk triage. Artinya, hasil ini membantu mengurutkan klaim mana yang layak ditinjau lebih dulu, bukan menggantikan keputusan verifikator.",
        items=[
            ("Severity dan tarif", "Kombinasi severity, tarif, dan lama rawat sering menjadi sinyal awal profil klaim yang menonjol."),
            ("Riwayat sebelum klaim", "Histori FKTP dan non-kapitasi membantu menempatkan klaim dalam konteks perilaku layanan sebelumnya."),
            ("Band prioritas", "Low, medium, dan high dibuat agar tim lebih mudah menerjemahkan skor menjadi urutan kerja."),
        ],
    )
    render_priority_legend()

input_data = {
    "fktp_hist_count_before": fktp_hist_count_before,
    "flag_kelas_upgrade": flag_kelas_upgrade,
    "flag_status_nonaktif": flag_status_nonaktif,
    "jumlah_diagnosis_sekunder": jumlah_diagnosis_sekunder,
    "lama_rawat_hari": lama_rawat_hari,
    "nonkap_hist_count_before": nonkap_hist_count_before,
    "severity_level_num": severity_level_num,
    "tarif_disetujui": tarif_disetujui,
    "total_special_cmg": total_special_cmg,
    "usia": usia,
}

if st.button("Hitung Skor Risiko", type="primary"):
    if api_ok:
        resp = score_single(input_data)
        priority = resp["priority"]
        risk_percent = resp["risk_percent"]
        risk_score = resp["risk_score"]
    else:
        from utils.scoring import score_dataframe

        result = score_dataframe(pd.DataFrame([input_data]))
        priority = result.iloc[0]["priority"]
        risk_percent = result.iloc[0]["risk_percent"]
        risk_score = result.iloc[0]["risk_score"]

    priority_kind = {"High Priority": "high", "Medium Priority": "medium", "Low Priority": "low"}
    priority_body = {
        "High Priority": "Klaim ini masuk prioritas verifikasi segera berdasarkan profil risiko yang relatif lebih kuat.",
        "Medium Priority": "Klaim ini layak mendapat perhatian lanjutan. Tinjau faktor dominan sebelum menentukan eskalasi.",
        "Low Priority": "Klaim ini berada pada profil risiko yang relatif lebih rendah menurut model saat ini.",
    }

    render_section_panel(
        kicker="Step 2",
        title="Assessment result",
        body="Gunakan hasil ini untuk membaca posisi klaim dalam antrian verifikasi, lalu konfirmasi dengan konteks operasional yang kamu pegang.",
    )

    render_result_hero(
        kind=priority_kind.get(priority, "neutral"),
        title=priority,
        score=f"{risk_percent:.2f}%",
        body=priority_body.get(priority, ""),
    )
    st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)
    render_metric_strip(
        [
            {"label": "Risk Score", "value": f"{risk_score:.3f}", "note": "probabilitas model", "strong": True},
            {"label": "Risk Percent", "value": f"{risk_percent:.2f}%", "note": "skala baca cepat"},
            {"label": "Threshold Medium", "value": f"{THRESHOLD_MEDIUM:.2f}", "note": "mulai perhatian lanjut"},
            {"label": "Threshold High", "value": f"{THRESHOLD_HIGH:.2f}", "note": "masuk prioritas tinggi"},
        ]
    )
    st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

    model = load_model()
    if hasattr(model, "feature_importances_"):
        feature_names = list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else USER_INPUT_FEATURES
        feat_imp = sorted(zip(feature_names, model.feature_importances_), key=lambda item: item[1], reverse=True)

        st.markdown('<div class="section-kicker">Interpretation</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top 3 Faktor Dominan</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Feature importance global menunjukkan sinyal yang paling sering memengaruhi arah prediksi model. Gunakan ini sebagai panduan interpretasi, bukan penjelasan kausal penuh untuk satu klaim.</div>',
            unsafe_allow_html=True,
        )

        imp_df = pd.DataFrame(
            {
                "Fitur": [FEATURE_LABELS.get(name, name) for name, _ in feat_imp[:3]],
                "Importance": [importance for _, importance in feat_imp[:3]],
            }
        )
        fig = px.bar(
            imp_df[::-1],
            x="Importance",
            y="Fitur",
            orientation="h",
            text=imp_df[::-1]["Importance"].apply(lambda value: f"{value:.1%}"),
            color="Importance",
            color_continuous_scale="teal",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="Importance",
            yaxis_title="",
            height=220,
        )
        apply_plotly_theme(fig, horizontal_grid=True, vertical_grid=False)
        st.plotly_chart(fig, width="stretch")

        for rank, (feature_name, feature_importance) in enumerate(feat_imp[:3], 1):
            label = FEATURE_LABELS.get(feature_name, feature_name)
            value = input_data.get(feature_name, "-")
            st.markdown(
                f"**{rank}. {label}** - nilai input: `{value}` | kontribusi model: **{feature_importance:.1%}**"
            )
    st.markdown('<div class="page-spacer page-spacer--sm"></div>', unsafe_allow_html=True)

    local_explanation = explain_single_claim(input_data, top_n=4)
    explanation_df = local_explanation["explanation_df"]
    display_explanation = explanation_df.copy()
    display_explanation["Fitur"] = display_explanation["feature"].map(lambda feature: FEATURE_LABELS.get(feature, feature))
    display_explanation["Nilai"] = display_explanation["feature_value"].astype(str)
    display_explanation["Arah"] = display_explanation["direction"].map(
        {"up": "Menaikkan risiko", "down": "Menurunkan risiko", "neutral": "Netral"}
    )
    display_explanation["Sumber"] = display_explanation["feature"].map(
        lambda feature: SOURCE_LABELS[classify_feature_source(feature)]
    )

    render_section_panel(
        kicker="Local Explanation",
        title="Drivers untuk klaim ini",
        body="Bagian ini bersifat kontekstual. Kontribusi di bawah dihitung khusus untuk klaim yang sedang dinilai, jadi bisa berbeda untuk tiap input meskipun modelnya sama.",
        soft=True,
    )

    explanation_chart_df = explanation_df.head(8).sort_values("contribution", ascending=True).copy()
    explanation_chart_df["Fitur"] = explanation_chart_df["feature"].map(
        lambda feature: FEATURE_LABELS.get(feature, feature)
    )
    explanation_chart_df["Jenis"] = explanation_chart_df["contribution"].apply(
        lambda value: "Mendorong naik" if value > 0 else "Menahan turun"
    )

    exp_fig = px.bar(
        explanation_chart_df,
        x="contribution",
        y="Fitur",
        orientation="h",
        color="Jenis",
        text=explanation_chart_df["contribution"].apply(lambda value: f"{value:+.3f}"),
        color_discrete_map={"Mendorong naik": "#d97a81", "Menahan turun": "#72b8a4"},
        title="Kontribusi lokal per fitur",
    )
    exp_fig.update_traces(textposition="outside")
    exp_fig.update_layout(
        showlegend=True,
        xaxis_title="Kontribusi SHAP (log-odds)",
        yaxis_title="",
        height=340,
    )
    apply_plotly_theme(exp_fig, horizontal_grid=True, vertical_grid=False)
    st.plotly_chart(exp_fig, width="stretch")

    displayed_sources = explanation_df.head(8)["feature"].map(classify_feature_source)
    source_counts = displayed_sources.value_counts()
    render_metric_strip(
        [
            {
                "label": "Input user",
                "value": str(int(source_counts.get("input_user", 0))),
                "note": "driver tampil dari field yang kamu isi di form",
                "strong": True,
            },
            {
                "label": "Turunan input",
                "value": str(int(source_counts.get("derived", 0))),
                "note": "dihitung dari kombinasi field inti",
            },
            {
                "label": "Default/fallback",
                "value": str(int(source_counts.get("default_fallback", 0))),
                "note": "field model yang belum dioverride di form ini",
            },
        ]
    )
    render_notice(
        "info",
        "Transparansi sumber driver",
        "Driver lokal dihitung dari input yang benar-benar masuk ke model. Jika sebuah fitur ditandai default atau fallback, artinya kontribusinya berasal dari nilai default yang dipakai dashboard saat field tersebut belum tersedia di form ini.",
    )

    up_col, down_col = st.columns(2, gap="large")
    with up_col:
        st.markdown('<div class="section-kicker">Drivers Up</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Faktor yang menaikkan risiko</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Fitur-fitur ini paling banyak mendorong skor klaim naik pada assessment saat ini.</div>',
            unsafe_allow_html=True,
        )
        if local_explanation["top_drivers_up"]:
            for index, row in enumerate(local_explanation["top_drivers_up"], 1):
                label = FEATURE_LABELS.get(row["feature"], row["feature"])
                source_label = SOURCE_LABELS[classify_feature_source(row["feature"])]
                st.markdown(
                    f"**{index}. {label}** - nilai: `{row['feature_value']}` | kontribusi: **+{row['contribution']:.3f}** | sumber: `{source_label}`"
                )
        else:
            st.caption("Tidak ada driver positif yang dominan pada klaim ini.")

    with down_col:
        st.markdown('<div class="section-kicker">Drivers Down</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Faktor yang menahan risiko</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Fitur-fitur ini paling kuat menahan skor agar tidak lebih tinggi pada klaim saat ini.</div>',
            unsafe_allow_html=True,
        )
        if local_explanation["top_drivers_down"]:
            for index, row in enumerate(local_explanation["top_drivers_down"], 1):
                label = FEATURE_LABELS.get(row["feature"], row["feature"])
                source_label = SOURCE_LABELS[classify_feature_source(row["feature"])]
                st.markdown(
                    f"**{index}. {label}** - nilai: `{row['feature_value']}` | kontribusi: **{row['contribution']:.3f}** | sumber: `{source_label}`"
                )
        else:
            st.caption("Tidak ada driver negatif yang dominan pada klaim ini.")

    with st.expander("Lihat detail input lengkap"):
        display = {FEATURE_LABELS.get(key, key): value for key, value in input_data.items()}
        display["Skor Risiko"] = risk_score
        display["Persentase Risiko"] = f"{risk_percent:.2f}%"
        display["Prioritas Verifikasi"] = priority
        st.dataframe(pd.DataFrame([display]), width="stretch")

    with st.expander("Lihat tabel explanation lengkap"):
        st.dataframe(
            display_explanation[["Fitur", "Nilai", "contribution", "abs_contribution", "Arah", "Sumber"]].rename(
                columns={
                    "contribution": "Kontribusi SHAP",
                    "abs_contribution": "Besar Kontribusi",
                }
            ),
            width="stretch",
            hide_index=True,
        )
