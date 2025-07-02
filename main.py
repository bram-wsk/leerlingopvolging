import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Leerlingen Markering", page_icon="📘", layout="centered")

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

if "naam" not in df_status.columns:
    df_status.reset_index(inplace=True)

df_status.set_index("naam", inplace=True)

# --- TITEL ---
st.title("📘 Leerlingen Markering Formulier")
st.caption("Geef maximaal 3 strepen per leerling. Bij 3 strepen wordt de status automatisch op 'Wachten op straf' gezet.")

# --- FORMULIER ---
invoer = []

for i, row in df.iterrows():
    naam = row["naam"]
    huidige_status = df_status.loc[naam, "status"] if naam in df_status.index else ""

    with st.container():
        col1, col2, col3 = st.columns([3, 2, 3])

        with col1:
            st.markdown(f"### 👤 {naam}")

        with col2:
            strepen = st.number_input(
                label="Aantal strepen",
                min_value=0,
                max_value=3,
                step=1,
                key=f"strepen_{i}"
            )

        with col3:
            if huidige_status == "wachten_op_straf":
                st.markdown("🟠 **Wachten op straf**")
            else:
                st.markdown("🟢 **Geen straf**")

    # ✅ Status logica
    if huidige_status != "wachten_op_straf" and strepen == 3:
        df_status.loc[naam, "status"] = "wachten_op_straf"

    # ❗ Straf afgehandeld-knop
    if df_status.loc[naam, "status"] == "wachten_op_straf":
        if st.button(f"✅ Straf afgehandeld: {naam}", key=f"straf_af_{i}"):
            df_status.loc[naam, "status"] = ""
            df_status.reset_index().to_csv(status_path, index=False)
            st.success(f"Strafstatus verwijderd voor {naam}")
            st.rerun()

    # Voeg invoer toe aan lijst
    if strepen > 0:
        invoer.append({
            "datum": datetime.today().strftime("%Y-%m-%d"),
            "naam": naam,
            "strepen": strepen
        })

# --- OPSLAAN ---
st.markdown("---")
if st.button("💾 Opslaan"):
    if invoer:
        df_nieuw = pd.DataFrame(invoer)
        df_nieuw.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))
        st.success("✅ Markeringen opgeslagen!")

        # Strafstatus bewaren
        df_status.reset_index().to_csv(status_path, index=False)

        st.rerun()
    else:
        st.warning("⚠️ Geen strepen ingevoerd. Niets opgeslagen.")

# --- DOWNLOAD ---
st.markdown("---")
if os.path.exists("markeringen.csv"):
    st.markdown("### ⬇️ Download markeringen")
    with open("markeringen.csv", "rb") as f:
        st.download_button(
            label="📥 Download markeringen.csv",
            data=f,
            file_name="markeringen.csv",
            mime="text/csv"
        )
