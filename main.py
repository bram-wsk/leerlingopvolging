import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIG --- 
SHEET_ID = "1AbCDeFgHiJkLmNoPqRsTuVwXyZ1234567890"  # <-- VERVANG DIT MET JOUW EIGEN SHEET ID
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
OUTPUT_BESTAND = "markeringen.csv"

# --- LAAD LEERLINGEN ---
@st.cache_data
def laad_leerlingen():
    try:
        df = pd.read_csv(SHEET_URL)
        if "naam" not in df.columns:
            st.error("❌ Kolom 'naam' ontbreekt in de sheet.")
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"❌ Fout bij het laden van leerlingen: {e}")
        return pd.DataFrame()

# --- STREAMLIT UI ---
st.title("📘 Leerlingen Markering Formulier")

df_leerlingen = laad_leerlingen()

if df_leerlingen.empty:
    st.stop()

# Selecteer leerling
naam = st.selectbox("Kies een leerling:", df_leerlingen["naam"].tolist())

reden = st.text_area("Reden van markering:")
strepen = st.number_input("Aantal strepen:", min_value=1, max_value=10, step=1)

if st.button("✅ Opslaan"):
    datum = datetime.today().strftime("%Y-%m-%d")
    nieuw = pd.DataFrame([{
        "datum": datum,
        "naam": naam,
        "reden": reden,
        "strepen": strepen
    }])
    nieuw.to_csv(OUTPUT_BESTAND, mode="a", index=False, header=not os.path.exists(OUTPUT_BESTAND))
    st.success("Markering succesvol opgeslagen!")
