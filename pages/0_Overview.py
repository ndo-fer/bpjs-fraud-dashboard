import streamlit as st

st.set_page_config(
    page_title="Overview",
    layout="wide"
)

st.title("Overview Dashboard")

st.write("""
Dashboard ini digunakan sebagai prototype decision-support
untuk membantu prioritas verifikasi klaim.
""")

st.warning(
    "Output model adalah indikasi risiko untuk prioritas verifikasi, bukan keputusan fraud final."
)

st.subheader("Fitur Dashboard")

st.markdown("""
- **Batch Upload**: upload CSV banyak klaim sekaligus.
- **Single Claim Scoring**: input satu klaim secara manual.
- **Risk Scoring**: menghasilkan skor risiko klaim.
- **Prioritas Verifikasi**: mengelompokkan klaim menjadi High, Medium, atau Low Priority.
- **Export Result**: hasil scoring dapat diunduh sebagai CSV.
""")

st.subheader("Catatan Akademik")

st.info("""
Dashboard ini merupakan prototype implementasi model machine learning.
Hasil prediksi digunakan untuk mendukung prioritas verifikasi, bukan sebagai keputusan final.
""")
