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

# --- INITIËLE STANDEN OPSLAAN ---
if "strepen" not in st.session_state:
    st.session_state.strepen = {naam: 0 for naam in df["naam"]}

st.title("📘 Leerlingen Markering Formulier")
st.write("Gebruik de knoppen om het aantal strepen per leerling aan te passen:")

for i, naam in enumerate(df["naam"]):
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f"**{naam}**")
    with col2:
        if st.button("➖", key=f"min_{i}"):
            if st.session_state.strepen[naam] > 0:
                st.session_state.strepen[naam] -= 1
    with col3:
        st.markdown(f"**{st.session_state.strepen[naam]}**")
    with col4:
        if st.button("➕", key=f"plus_{i}"):
            if st.session_state.strepen[naam] < 10:
                st.session_state.strepen[naam] += 1

# --- OPSLAAN ---
if st.button("✅ Opslaan"):
    invoer = []
    for naam, aantal in st.session_state.strepen.items():
        if aantal > 0:
            invoer.append({
                "datum": datetime.today().strftime("%Y-%m-%d"),
                "naam": naam,
                "strepen": aantal
            })

    if invoer:
        df_nieuw = pd.DataFrame(invoer)
        df_nieuw.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))
        st.success("✅ Markeringen opgeslagen!")
        # Reset de waarden
        for naam in st.session_state.strepen:
            st.session_state.strepen[naam] = 0
    else:
        st.warning("⚠️ Geen strepen ingevoerd. Niets opgeslagen.")

# --- OVERZICHT ---
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
