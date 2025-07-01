import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIG ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mY3AZgVQ53OATWh1Zir7_nnnTcVyLbjPSs9F8PJK9BA/export?format=csv"
OUTPUT_BESTAND = "markeringen.csv"

# --- DATA LADEN ---
try:
    df = pd.read_csv(SHEET_URL)
    st.success("✅ Verbonden met Google Sheet!")
except Exception as e:
    st.error(f"❌ Fout bij laden: {e}")
    st.stop()

# --- FORMULIER ---
st.title("📘 Leerlingen Markering Formulier")

if "naam" not in df.columns:
    st.error("❌ Kolom 'naam' ontbreekt in de sheet.")
    st.stop()

leerling = st.selectbox("Kies een leerling:", df["naam"].tolist())
reden = st.text_area("Reden van markering:")
strepen = st.number_input("Aantal strepen:", min_value=1, max_value=10, step=1)

if st.button("✅ Opslaan"):
    datum = datetime.today().strftime("%Y-%m-%d")
    nieuw = pd.DataFrame([{
        "datum": datum,
        "naam": leerling,
        "reden": reden,
        "strepen": strepen
    }])
    nieuw.to_csv(OUTPUT_BESTAND, mode="a", index=False, header=not os.path.exists(OUTPUT_BESTAND))
    st.success("✅ Markering opgeslagen!")
