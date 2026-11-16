"""AVESONIC: dashboard pengenalan spesies burung Indonesia dari suara.

Jalankan:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="AVESONIC · Mengenali burung dari suaranya", page_icon="🪶", layout="wide", initial_sidebar_state="expanded")

from avesonic import tema                                      # noqa: E402
from avesonic.halaman import beranda, data, prediksi, hasil, tentang   # noqa: E402

tema.pasang_css()
st.logo("aset/logo.svg", size="large")

HAL = {
    "beranda": st.Page(beranda.tampil, title="Beranda", url_path="beranda", default=True),
    "data": st.Page(data.tampil, title="Kenali Datanya", url_path="data"),
    "tebak": st.Page(prediksi.tampil, title="Coba Tebak", url_path="tebak"),
    "hasil": st.Page(hasil.tampil, title="Hasil Analisis", url_path="hasil"),
    "catatan": st.Page(tentang.tampil, title="Catatan & Sumber", url_path="catatan"),
}
st.session_state["_hal"] = HAL
halaman = st.navigation(list(HAL.values()))
tema.sidebar()
halaman.run()
tema.kaki()
