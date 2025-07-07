import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

st.set_page_config(page_title="Leerlingen Markering", page_icon="\ud83d\udcd8", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .stNumberInput input {
        text-align: center;
    }
    .stDateInput {
        padding-top: 0.2rem;
    }
    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 0.4em 0 0.8em;
    }
</style>
""", unsafe_allow_html=True)

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
        st.error("\u274c Kolom 'naam' ontbreekt.")
        st.stop()
except Exception as e:
    st.error(f"\u274c Fout bij inlezen van leerlingen: {e}")
    st.stop()

# --- LAAD STRAFSTATUS OF INITIALISEER ---
status_path = "strafstatus.csv"
if os.path.exists(status_path):
    df_status = pd.read_csv(status_path, dtype=str)
    for kolom in ["strafdatum", "verdubbel_datum", "laatst_bijgewerkt", "strepen"]:
        if kolom not in df_status.columns:
            df_status[kolom] = "" if kolom != "strepen" else "0"
else:
    df_status = pd.DataFrame({
        "naam": df["naam"],
        "status": "",
        "strafdatum": "",
        "verdubbel_datum": "",
        "laatst_bijgewerkt": "",
        "strepen": "0"
    })
    df_status.to_csv(status_path, index=False)

df_status = herstel_index(df_status)

# --- CONTROLEER OP VERDUBBELING EN STRAFSTUDIE ---
nu = datetime.now(ZoneInfo("Europe/Brussels"))
gewijzigd = False

for naam in df_status.index:
    status = df_status.loc[naam, "status"]

    if status == "wachten_op_straf":
        datum_str = df_status.loc[naam, "strafdatum"]
        if datum_str:
            try:
                strafmoment = datetime.strptime(datum_str, "%d/%m/%Y").replace(tzinfo=ZoneInfo("Europe/Brussels")) + timedelta(hours=16, minutes=59)
                if nu >= strafmoment:
                    df_status.loc[naam, "status"] = "verdubbeld"
                    df_status.loc[naam, "verdubbel_datum"] = (nu + timedelta(days=1)).strftime("%d/%m/%Y")
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    gewijzigd = True
            except ValueError:
                pass

    elif status == "verdubbeld":
        datum_str = df_status.loc[naam, "verdubbel_datum"]
        if datum_str:
            try:
                strafmoment = datetime.strptime(datum_str, "%d/%m/%Y").replace(tzinfo=ZoneInfo("Europe/Brussels")) + timedelta(hours=16, minutes=59)
                if nu >= strafmoment:
                    df_status.loc[naam, "status"] = "strafstudie"
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    gewijzigd = True
            except ValueError:
                pass

if gewijzigd:
    df_status.reset_index().to_csv(status_path, index=False)
    df_status = herstel_index(df_status)

# --- TITEL + HEADERS ---
st.title("\ud83d\udcd8 Leerlingen Markering Formulier")
st.caption("Geef maximaal 3 strepen per leerling. Bij 3 strepen wordt automatisch 'wachten op straf' ingesteld.")

header1, header2, header3, header4 = st.columns([3, 1.2, 2, 2])
with header1:
    st.markdown("**\ud83d\udc64 Naam**")
with header2:
    st.markdown("**\ud83d\udcc8 Strepen**")
with header3:
    st.markdown("**\ud83d\udccd Status**")
with header4:
    st.markdown("**\u2699\ufe0f Actie**")

log_strepen = []

for i, row in df.iterrows():
    naam = row["naam"]
    huidige_status = df_status.loc[naam, "status"] if naam in df_status.index else ""

    col1, col2, col3, col4 = st.columns([3, 1.2, 2, 2])

    with col1:
        st.markdown(f"{naam}")

    with col2:
        try:
            vorige_strepen = int(df_status.loc[naam, "strepen"])
        except (KeyError, ValueError, TypeError):
            vorige_strepen = 0

        strepen = st.number_input("", 0, 3, value=vorige_strepen, step=1, key=f"strepen_{i}")

        if huidige_status not in ["wachten_op_straf", "verdubbeld", "strafstudie"]:
            if strepen == 3:
                df_status.loc[naam, "status"] = "wachten_op_straf"
                df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                huidige_status = "wachten_op_straf"
            else:
                df_status.loc[naam, "status"] = huidige_status

        df_status.loc[naam, "strepen"] = str(strepen)

    with col3:
        status_tekst = {
            "wachten_op_straf": "\ud83d\udfe0 **Wachten op straf**",
            "verdubbeld": "\ud83d\udd34 **Verdubbeld**",
            "strafstudie": "\u26ab **Strafstudie**"
        }.get(huidige_status, "\ud83d\udfe2 **Geen straf**")
        st.markdown(status_tekst)

    with col4:
        if huidige_status == "wachten_op_straf":
            huidige_datum_str = df_status.loc[naam, "strafdatum"]
            try:
                huidige_datum = datetime.strptime(huidige_datum_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                huidige_datum = (nu + timedelta(days=1)).date()

            col_datum, col_knop = st.columns([4, 1])
            with col_datum:
                gekozen_datum = st.date_input("", value=huidige_datum, key=f"datum_{i}")
                nieuwe_datum = gekozen_datum.strftime("%d/%m/%Y")
                if df_status.loc[naam, "strafdatum"] != nieuwe_datum:
                    df_status.loc[naam, "strafdatum"] = nieuwe_datum
                    df_status.reset_index().to_csv(status_path, index=False)
                    df_status = herstel_index(df_status)

            with col_knop:
                st.markdown("&nbsp;")
                if st.button("\u2705", key=f"straf_af_{i}"):
                    for kol in ["status", "strafdatum", "verdubbel_datum"]:
                        df_status.loc[naam, kol] = ""
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    df_status.reset_index().to_csv(status_path, index=False)
                    st.success(f"Strafstatus verwijderd voor {naam}")
                    st.rerun()

        elif huidige_status == "verdubbeld":
            huidige_datum_str = df_status.loc[naam, "verdubbel_datum"]
            try:
                huidige_datum = datetime.strptime(huidige_datum_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                huidige_datum = (nu + timedelta(days=1)).date()

            col_datum, col_knop = st.columns([4, 1])
            with col_datum:
                gekozen_datum = st.date_input("", value=huidige_datum, key=f"verdubbel_datum_{i}")
                nieuwe_datum = gekozen_datum.strftime("%d/%m/%Y")
                if df_status.loc[naam, "verdubbel_datum"] != nieuwe_datum:
                    df_status.loc[naam, "verdubbel_datum"] = nieuwe_datum
                    df_status.reset_index().to_csv(status_path, index=False)
                    df_status = herstel_index(df_status)
                if gekozen_datum <= datetime.now().date():
                    st.warning("\u26a0\ufe0f Strafdatum is vandaag of in het verleden.")

            with col_knop:
                st.markdown("&nbsp;")
                if st.button("\u2705", key=f"verdubbel_af_{i}"):
                    for kol in ["status", "strafdatum", "verdubbel_datum"]:
                        df_status.loc[naam, kol] = ""
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    df_status.reset_index().to_csv(status_path, index=False)
                    st.success(f"Verdubbeling verwijderd voor {naam}")
                    st.rerun()

        elif huidige_status == "strafstudie":
            col_info, col_knop = st.columns([4, 1])
            with col_info:
                st.info("Niet gereageerd op verdubbelde straf.")
            with col_knop:
                st.markdown("&nbsp;")
                if st.button("\ud83d\udcde", key=f"ouders_opgebeld_{i}"):
                    for kol in ["status", "strafdatum", "verdubbel_datum"]:
                        df_status.loc[naam, kol] = ""
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    df_status.reset_index().to_csv(status_path, index=False)
                    st.success(f"Status op groen gezet na contact met ouders ({naam})")
                    st.rerun()

    if strepen > 0:
        log_strepen.append({
            "datum": datetime.now(ZoneInfo("Europe/Brussels")).strftime("%Y-%m-%d"),
            "naam": naam,
            "strepen": strepen
        })

    st.markdown("<hr style='margin: 0.2em 0;'>", unsafe_allow_html=True)

# --- OPSLAAN ---
st.markdown("---")
if st.button("\ud83d\udcc5 Opslaan"):
    if log_strepen:
        df_log = pd.DataFrame(log_strepen)
        df_log.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))

    df_status.reset_index().to_csv(status_path, index=False)
    st.success("\u2705 Wijzigingen opgeslagen!")
    st.rerun()

# --- DOWNLOADKNOP ---
st.markdown("---")
if os.path.exists("markeringen.csv"):
    st.markdown("### \ud83d\udcc5 Download markeringen")
    with open("markeringen.csv", "rb") as f:
        st.download_button(
            label="\u2b07\ufe0f Download markeringen.csv",
            data=f,
            file_name="markeringen.csv",
            mime="text/csv"
        )
