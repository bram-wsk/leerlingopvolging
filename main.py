import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURATIE ---
SHEET_ID = "JOUW_SHEET_ID_HIER"  # Vervang dit!
SHEET_LEES_TAB = "Leerlingen"
SHEET_SCHRIJF_TAB = "Markeringen"
JSON_KEY = "service_account.json"

# --- AUTHENTICATIE ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY, scope)
client = gspread.authorize(creds)

# --- LEES LEERLINGEN ---
try:
    leerlingen_ws = client.open_by_key(SHEET_ID).worksheet(SHEET_LEES_TAB)
    leerlingen_data = leerlingen_ws.get_all_records()
    df_leerlingen = pd.DataFrame(leerlingen_data)
except Exception as e:
    st.error(f"❌ Fout bij lezen leerlingen: {e}")
    st.stop()

# --- STREAMLIT FORMULIER ---
st.title("📘 Leerlingen Markering Formulier")

if df_leerlingen.empty or "naam" not in df_leerlingen.columns:
    st.error("❌ Geen geldige 'naam'-kolom in het tabblad 'Leerlingen'.")
    st.stop()

naam = st.selectbox("Kies een leerling:", df_leerlingen["naam"])
reden = st.text_area("Reden van markering:")
strepen = st.number_input("Aantal strepen:", min_value=1, max_value=10, step=1)

if st.button("✅ Opslaan"):
    try:
        schrijf_ws = client.open_by_key(SHEET_ID).worksheet(SHEET_SCHRIJF_TAB)
        schrijf_ws.append_row([
            datetime.today().strftime("%Y-%m-%d"),
            naam,
            reden,
            strepen
        ])
        st.success("✅ Markering opgeslagen in Google Sheet!")
    except Exception as e:
        st.error(f"❌ Fout bij opslaan: {e}")
