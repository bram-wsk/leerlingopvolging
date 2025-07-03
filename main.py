import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

st.set_page_config(page_title="Leerlingen Markering", page_icon="📘", layout="centered")

# --- HULPFUNCTIE ---
def herstel_index(df):
    if "naam" not in df.columns:
        df.reset_index(drop=False, inplace=True)
    if "naam" in df.columns:
        df.set_index("naam", inplace=True)
    return df

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

    # Upgrade oude structuur indien nodig
    if "status" in df_status.columns:
        df_status["strafwerk"] = df_status["status"].apply(lambda x: "ja" if x == "wachten_op_straf" else "nee")
        df_status["verdubbeld"] = df_status["status"].apply(lambda x: "ja" if x == "verdubbeld" else "nee")
        df_status.drop(columns=["status"], inplace=True)
        df_status.to_csv(status_path, index=False)

    if "strafdatum" not in df_status.columns:
        df_status["strafdatum"] = ""
    if "strafwerk" not in df_status.columns:
        df_status["strafwerk"] = "nee"
    if "verdubbeld" not in df_status.columns:
        df_status["verdubbeld"] = "nee"
else:
    df_status = pd.DataFrame({
        "naam": df["naam"],
        "strafwerk": "nee",
        "verdubbeld": "nee",
        "strafdatum": ""
    })
    df_status.to_csv(status_path, index=False)

df_status = herstel_index(df_status)

# --- CONTROLEER OP VERDUBBELING ---
nu = datetime.now(ZoneInfo("Europe/Brussels"))
gewijzigd = False
for naam in df_status.index:
    strafwerk = df_status.loc[naam, "strafwerk"]
    verdubbeld = df_status.loc[naam, "verdubbeld"]
    datum_str = df_status.loc[naam, "strafdatum"]

    if strafwerk == "ja" and verdubbeld != "ja" and datum_str:
        try:
            strafmoment = datetime.strptime(datum_str, "%d/%m/%Y").replace(tzinfo=ZoneInfo("Europe/Brussels")) + timedelta(hours=9, minutes=27)
            if nu >= strafmoment:
                df_status.loc[naam, "verdubbeld"] = "ja"
                gewijzigd = True
        except ValueError:
            pass

if gewijzigd:
    df_status.reset_index().to_csv(status_path, index=False)
    df_status = herstel_index(df_status)

# --- TITEL ---
st.title("📘 Leerlingen Markering Formulier")
st.caption("Geef maximaal 3 strepen per leerling. Bij 3 strepen wordt automatisch 'strafwerk' ingesteld.")

# --- FORMULIER ---
invoer = []

for i, row in df.iterrows():
    naam = row["naam"]
    strafwerk = df_status.loc[naam, "strafwerk"]
    verdubbeld = df_status.loc[naam, "verdubbeld"]

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

        if strafwerk != "ja" and verdubbeld != "ja":
            if strepen == 3:
                df_status.loc[naam, "strafwerk"] = "ja"
                df_status.loc[naam, "verdubbeld"] = "nee"

    with col3:
        if verdubbeld == "ja":
            st.markdown("🔴 **Straf verdubbeld**")

        elif strafwerk == "ja":
            st.markdown("🟠 **Staat op straf**")

            huidige_datum_str = df_status.loc[naam, "strafdatum"]
            try:
                huidige_datum = datetime.strptime(huidige_datum_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                huidige_datum = (nu + timedelta(days=1)).date()

            gekozen_datum = st.date_input(
                "📅 Kies strafdatum",
                value=huidige_datum,
                key=f"datum_{i}"
            )

            nieuwe_datum = gekozen_datum.strftime("%d/%m/%Y")
            if df_status.loc[naam, "strafdatum"] != nieuwe_datum:
                df_status.loc[naam, "strafdatum"] = nieuwe_datum
                df_status.reset_index().to_csv(status_path, index=False)
                df_status = herstel_index(df_status)

            if st.button("✅ Straf afgehandeld", key=f"straf_af_{i}"):
                df_status.loc[naam, "strafwerk"] = "nee"
                df_status.loc[naam, "verdubbeld"] = "nee"
                df_status.loc[naam, "strafdatum"] = ""
                df_status.reset_index().to_csv(status_path, index=False)
                st.success(f"Strafstatus verwijderd voor {naam}")
                st.rerun()

        else:
            st.markdown("🟢 **Geen straf**")

    if strepen > 0:
        invoer.append({
            "datum": nu.strftime("%Y-%m-%d"),
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
