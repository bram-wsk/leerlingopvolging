import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- LEES LEERLINGEN ---
try:
    df = pd.read_csv("leerlingen.csv")
    if "naam" not in df.columns:
        st.error("❌ Kolom 'naam' ontbreekt.")
        st.stop()
except Exception as e:
    st.error(f"❌ Fout bij inlezen van leerlingen: {e}")
    st.stop()

# --- FORMULIER ---
st.title("📘 Leerlingen Markering Formulier")

naam = st.selectbox("Kies een leerling:", df["naam"])
reden = st.text_area("Reden van markering:")
strepen = st.number_input("Aantal strepen:", 1, 10, step=1)

if st.button("✅ Opslaan"):
    datum = datetime.today().strftime("%Y-%m-%d")
    nieuw = pd.DataFrame([{
        "datum": datum,
        "naam": naam,
        "reden": reden,
        "strepen": strepen
    }])
    nieuw.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))
    st.success("✅ Markering opgeslagen!")
