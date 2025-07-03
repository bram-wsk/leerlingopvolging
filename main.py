import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
    df_status = pd.read_csv(status_path, dtype=str)
    if "strafdatum" not in df_status.columns:
        df_status["strafdatum"] = ""
else:
    df_status = pd.DataFrame({"naam": df["naam"], "status": "", "strafdatum": ""})
    df_status.to_csv(status_path, index=False)

if "naam" not in df_status.columns:
    df_status.reset_index(inplace=True)

df_status.set_index("naam", inplace=True)

# --- CONTROLEER OP VERDUBBELING ---
nu = datetime.now()
gewijzigd = False
for naam in df_status.index:
    status = df_status.loc[naam, "status"]
    datum_str = df_status.loc[naam, "strafdatum"]

    if status == "wachten_op_straf" and datum_str:
        try:
            strafmoment = datetime.strptime(datum_str, "%d/%m/%Y") + timedelta(hours=16, minutes=15)
            if nu >= strafmoment:
                df_status.loc[naam, "status"] = "verdubbeld"
                gewijzigd = True
        except ValueError:
            pass

# --- Sla meteen op als iets aangepast werd ---
if gewijzigd:
    df_status.reset_index().to_csv(status_path, index=False)
    df_status.set_index("naam", inplace=True)

# --- TITEL ---
st.title("📘 Leerlingen Markering Formulier")
st.caption("Geef maximaal 3 strepen per leerling. Bij 3 strepen wordt automatisch 'wachten op straf' ingesteld.")

# --- FORMULIER ---
invoer = []

for i, row in df.iterrows():
    naam = row["naam"]
    huidige_status = df_status.loc[naam, "status"] if naam in df_status.index else ""

    col1, col2, col3 = st.columns([3, 2, 4])

    with col1:
        st.markdown(f"### 👤 {naam}")

    with col2:
        strepen = st.number_input(
            label="",
            min_value=0,
            max_value=3,
            step=1,
            key=f"strepen_{i}"
        )

        if huidige_status not in ["wachten_op_straf", "verdubbeld"]:
            if strepen == 3:
                df_status.loc[naam, "status"] = "wachten_op_straf"
                huidige_status = "wachten_op_straf"
            else:
                df_status.loc[naam, "status"] = huidige_status

    with col3:
        if huidige_status == "wachten_op_straf":
            st.markdown("🟠 **Wachten op straf**")

            # Bestaande strafdatum ophalen, of standaard morgen
            huidige_datum_str = df_status.loc[naam, "strafdatum"]
            try:
                huidige_datum = datetime.strptime(huidige_datum_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                huidige_datum = (datetime.today() + timedelta(days=1)).date()

            gekozen_datum = st.date_input(
                "📅 Kies strafdatum",
                value=huidige_datum,
                key=f"datum_{i}"
            )

            nieuwe_datum = gekozen_datum.strftime("%d/%m/%Y")
            if df_status.loc[naam, "strafdatum"] != nieuwe_datum:
                df_status.loc[naam, "strafdatum"] = nieuwe_datum
                df_status.reset_index().to_csv(status_path, index=False)
                df_status.set_index("naam", inplace=True)

            if st.button("✅ Straf afgehandeld", key=f"straf_af_{i}"):
                df_status.loc[naam, "status"] = ""
                df_status.loc[naam, "strafdatum"] = ""
                df_status.reset_index().to_csv(status_path, index=False)
                st.success(f"Strafstatus verwijderd voor {naam}")
                st.rerun()

        elif huidige_status == "verdubbeld":
            st.markdown("🔴 **Straf verdubbeld**")

        else:
            st.markdown("🟢 **Geen straf**")

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

        df_status.reset_index().to_csv(status_path, index=False)

        st.rerun()
    else:
        st.warning("⚠️ Geen strepen ingevoerd. Niets opgeslagen.")

# --- DOWNLOADKNOP ---
st.markdown("---")
if os.path.exists("markeringen.csv"):
    st.markdown("### 📥 Download markeringen")
    with open("markeringen.csv", "rb") as f:
        st.download_button(
            label="⬇️ Download markeringen.csv",
            data=f,
            file_name="markeringen.csv",
            mime="text/csv"
        )
