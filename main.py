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

st.write("Voer het aantal strepen in voor elke leerling:")

invoer = []

for i, row in df.iterrows():
    naam = row["naam"]
    strepen = st.number_input(
        label=f"{naam}",
        min_value=0,
        max_value=10,
        step=1,
        key=f"strepen_{i}"
    )
    if strepen > 0:
        invoer.append({
            "datum": datetime.today().strftime("%Y-%m-%d"),
            "naam": naam,
            "strepen": strepen
        })

if st.button("✅ Opslaan"):
    if invoer:
        df_nieuw = pd.DataFrame(invoer)
        df_nieuw.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))
        st.success("✅ Markeringen opgeslagen!")
    else:
        st.warning("⚠️ Geen strepen ingevoerd. Niets opgeslagen.")

# --- OVERZICHT TONEN ALS BESTAND BESTAAT ---
if os.path.exists("markeringen.csv"):
    st.subheader("📊 Overzicht van ingevoerde markeringen")
    df_mark = pd.read_csv("markeringen.csv")
    st.dataframe(df_mark)

    with open("markeringen.csv", "rb") as f:
        st.download_button(
            label="⬇️ Download markeringen",
            data=f,
            file_name="markeringen.csv",
            mime="text/csv"
        )
