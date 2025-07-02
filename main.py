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

# --- LAAD STRAFSTATUS OF INITIALISEER ---
status_path = "strafstatus.csv"
if os.path.exists(status_path):
    df_status = pd.read_csv(status_path)
else:
    df_status = pd.DataFrame({"naam": df["naam"], "status": ""})
    df_status.to_csv(status_path, index=False)

# Zorg dat 'naam' een kolom blijft
if "naam" not in df_status.columns:
    df_status.reset_index(inplace=True)

df_status.set_index("naam", inplace=True)

# --- FORMULIER ---
st.title("📘 Leerlingen Markering Formulier")
st.write("Voer het aantal strepen in voor elke leerling (max. 3):")

invoer = []

for i, row in df.iterrows():
    naam = row["naam"]

    col1, col2, col3 = st.columns([3, 2, 3])

    with col1:
        st.markdown(f"**{naam}**")

    with col2:
        strepen = st.number_input(
            label="",
            min_value=0,
            max_value=3,
            step=1,
            key=f"strepen_{i}"
        )

    # Huidige status ophalen
    huidige_status = df_status.loc[naam, "status"] if naam in df_status.index else ""

    # ✅ Zet status enkel als hij nog niet op 'wachten_op_straf' staat én 3 strepen zijn ingevoerd
    if huidige_status != "wachten_op_straf" and strepen == 3:
        df_status.loc[naam, "status"] = "wachten_op_straf"

    # ❗ Toon status en knop alleen als status momenteel 'wachten_op_straf' is
    if df_status.loc[naam, "status"] == "wachten_op_straf":
        col3.markdown("🟠 *Wachten op straf*")

        if st.button(f"Straf afgehandeld: {naam}", key=f"straf_af_{i}"):
            df_status.loc[naam, "status"] = ""
            df_status.reset_index().to_csv(status_path, index=False)
            st.success(f"✅ Strafstatus verwijderd voor {naam}")
            st.rerun()

    # Verzamel invoer
    if strepen > 0:
        invoer.append({
            "datum": datetime.today().strftime("%Y-%m-%d"),
            "naam": naam,
            "strepen": strepen
        })

# --- OPSLAAN ---
if st.button("✅ Opslaan"):
    if invoer:
        df_nieuw = pd.DataFrame(invoer)
        df_nieuw.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))
        st.success("✅ Markeringen opgeslagen!")

        # Strafstatus bewaren
        df_status.reset_index().to_csv(status_path, index=False)

        st.rerun()
    else:
        st.warning("⚠️ Geen strepen ingevoerd. Niets opgeslagen.")

# --- DOWNLOADKNOP ---
if os.path.exists("markeringen.csv"):
    with open("markeringen.csv", "rb") as f:
        st.download_button(
            label="⬇️ Download markeringen",
            data=f,
            file_name="markeringen.csv",
            mime="text/csv"
        )
