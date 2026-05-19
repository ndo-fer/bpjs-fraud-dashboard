import streamlit as st

from utils.schema import FEATURES, FEATURE_LABELS

st.set_page_config(
    page_title="Artifacts & Notes",
    layout="wide"
)

st.title("Artifacts & Notes")

st.subheader("Model Artifact")

st.code("models/winner_model.joblib")

st.write("Model yang digunakan adalah model XGBoost classifier hasil training sebelumnya.")

st.subheader("Input Features")

for feature in FEATURES:
    st.markdown(f"- **{FEATURE_LABELS.get(feature, feature)}** {feature}")

st.subheader("Priority Threshold")

st.markdown("""
- **High Priority**: skor risiko >= 70%
- **Medium Priority**: skor risiko >= 40% dan < 70%
- **Low Priority**: skor risiko < 40%
""")

st.subheader("Disclaimer")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

st.info(
    "Dashboard ini digunakan sebagai prototype akademik untuk menunjukkan implementasi model machine learning ke dalam sistem decision-support."
)
