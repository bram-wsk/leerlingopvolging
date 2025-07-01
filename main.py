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
strepen = st.number_input("Aantal strepen:", min_value=1, max_value=10, step=1)

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

# --- OVERZICHT TONEN ALS BESTAND BESTAAT ---
if os.path.exists("markeringen.csv"):
    st.subheader("📊 Overzicht van ingevoerde markeringen")
    df_mark = pd.read_csv("markeringen.csv")
    st.dataframe(df_mark)

    # --- DOWNLOADKNOP ---
    with open("markeringen.csv", "rb") as f:
        st.download_button(
            label="⬇️ Download markeringen",
            data=f,
            file_name="markeringen.csv",
            mime="text/csv"
        )
