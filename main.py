import streamlit as st  
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

st.set_page_config(page_title="Leerlingen Markering", page_icon="📘", layout="wide")

# --- STYLING ---
st.markdown("""
<style>
    .element-container:has(input) {
        padding-top: 0.5rem;
    }
    input[type=number] {
        text-align: center;
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
        st.error("❌ Kolom 'naam' ontbreekt.")
        st.stop()
except Exception as e:
    st.error(f"❌ Fout bij inlezen van leerlingen: {e}")
    st.stop()

# --- LAAD STRAFSTATUS ---
status_path = "strafstatus.csv"
if os.path.exists(status_path):
    df_status = pd.read_csv(status_path, dtype=str)
    if "strafdatum" not in df_status.columns:
        df_status["strafdatum"] = ""
    if "verdubbel_datum" not in df_status.columns:
        df_status["verdubbel_datum"] = ""
    if "laatst_bijgewerkt" not in df_status.columns:
        df_status["laatst_bijgewerkt"] = ""
    if "strepen" not in df_status.columns:
        df_status["strepen"] = "0"
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

# --- CONTROLE OP STATUSOVERGANG ---
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

# --- TITEL ---
st.title("📘 Leerlingen Markering Formulier")
st.caption("Geef maximaal 3 strepen per leerling. Bij 3 strepen wordt automatisch 'wachten op straf' ingesteld.")

# --- FORMULIER ---
log_strepen = []

# Kolomtitels boven de tabel
kop = st.columns([3, 1.2, 2, 2])
with kop[0]: st.markdown("**👤 Naam**")
with kop[1]: st.markdown("**✏️ Strepen**")
with kop[2]: st.markdown("**📍 Status**")
with kop[3]: st.markdown("**📅 Actie / Datum**")

for i, row in df.iterrows():
    naam = row["naam"]
    huidige_status = df_status.loc[naam, "status"] if naam in df_status.index else ""

    # Bepaal status-emoji
    if huidige_status == "wachten_op_straf":
        status_emoji = "🟠 Wachten op straf"
    elif huidige_status == "verdubbeld":
        status_emoji = "🔴 Verdubbeld"
    elif huidige_status == "strafstudie":
        status_emoji = "⚫ Strafstudie"
    else:
        status_emoji = "🟢 Geen straf"

    rij = st.columns([3, 1.2, 2, 2])
    with rij[0]:
        st.markdown(f"### {naam}")

    with rij[1]:
        try:
            vorige_strepen = int(df_status.loc[naam, "strepen"])
        except (KeyError, ValueError, TypeError):
            vorige_strepen = 0

        strepen = st.number_input("", min_value=0, max_value=3, step=1, value=vorige_strepen, key=f"strepen_{i}")

        if huidige_status not in ["wachten_op_straf", "verdubbeld", "strafstudie"]:
            if strepen == 3:
                df_status.loc[naam, "status"] = "wachten_op_straf"
                df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                huidige_status = "wachten_op_straf"
                status_emoji = "🟠 Wachten op straf"
            else:
                df_status.loc[naam, "status"] = huidige_status

        df_status.loc[naam, "strepen"] = str(strepen)

    with rij[2]:
        col_status = st.columns([1])
        with col_status[0]:
            st.markdown(f"<div style='padding-top: 12px'><strong>{status_emoji}</strong></div>", unsafe_allow_html=True)

    with rij[3]:
        if huidige_status == "wachten_op_straf":
            huidige_datum_str = df_status.loc[naam, "strafdatum"]
            try:
                huidige_datum = datetime.strptime(huidige_datum_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                huidige_datum = (nu + timedelta(days=1)).date()

            col_datum, col_knop = st.columns([4, 1])
            with col_datum:
                gekozen_datum = st.date_input(label="", value=huidige_datum, key=f"datum_{i}")
                nieuwe_datum = gekozen_datum.strftime("%d/%m/%Y")
                if df_status.loc[naam, "strafdatum"] != nieuwe_datum:
                    df_status.loc[naam, "strafdatum"] = nieuwe_datum
                    df_status.reset_index().to_csv(status_path, index=False)
                    df_status = herstel_index(df_status)

            with col_knop:
                st.markdown("<div style='padding-top: 10px'>", unsafe_allow_html=True)
                if st.button("✅", key=f"straf_af_{i}"):
                    df_status.loc[naam, "status"] = ""
                    df_status.loc[naam, "strafdatum"] = ""
                    df_status.loc[naam, "verdubbel_datum"] = ""
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    df_status.reset_index().to_csv(status_path, index=False)
                    st.success(f"Strafstatus verwijderd voor {naam}")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        elif huidige_status == "verdubbeld":
            huidige_datum_str = df_status.loc[naam, "verdubbel_datum"]
            try:
                huidige_datum = datetime.strptime(huidige_datum_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                huidige_datum = (nu + timedelta(days=1)).date()

            col_datum, col_knop = st.columns([4, 1])
            with col_datum:
                gekozen_datum = st.date_input(label="", value=huidige_datum, key=f"verdubbel_datum_{i}")
                nieuwe_datum = gekozen_datum.strftime("%d/%m/%Y")
                if df_status.loc[naam, "verdubbel_datum"] != nieuwe_datum:
                    df_status.loc[naam, "verdubbel_datum"] = nieuwe_datum
                    df_status.reset_index().to_csv(status_path, index=False)
                    df_status = herstel_index(df_status)

                if gekozen_datum <= datetime.now().date():
                    st.warning("⚠️ Deze strafdatum is vandaag of in het verleden. Actie vereist!")

            with col_knop:
                st.markdown("<div style='padding-top: 10px'>", unsafe_allow_html=True)
                if st.button("✅", key=f"verdubbel_af_{i}"):
                    df_status.loc[naam, "status"] = ""
                    df_status.loc[naam, "strafdatum"] = ""
                    df_status.loc[naam, "verdubbel_datum"] = ""
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    df_status.reset_index().to_csv(status_path, index=False)
                    st.success(f"Verdubbeling verwijderd voor {naam}")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        elif huidige_status == "strafstudie":
            col_info, col_knop = st.columns([4, 1])
            with col_info:
                st.info("Niet gereageerd op verdubbelde straf.")
            with col_knop:
                st.markdown("<div style='padding-top: 10px'>", unsafe_allow_html=True)
                if st.button("📞", key=f"ouders_opgebeld_{i}"):
                    df_status.loc[naam, "status"] = ""
                    df_status.loc[naam, "strafdatum"] = ""
                    df_status.loc[naam, "verdubbel_datum"] = ""
                    df_status.loc[naam, "laatst_bijgewerkt"] = nu.strftime("%Y-%m-%d")
                    df_status.reset_index().to_csv(status_path, index=False)
                    st.success(f"Status op groen gezet na contact met ouders ({naam})")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    if strepen > 0:
        log_strepen.append({
            "datum": datetime.now(ZoneInfo("Europe/Brussels")).strftime("%Y-%m-%d"),
            "naam": naam,
            "strepen": strepen
        })

# --- OPSLAAN ---
st.markdown("---")
if st.button("💾 Opslaan"):
    if log_strepen:
        df_log = pd.DataFrame(log_strepen)
        df_log.to_csv("markeringen.csv", mode="a", index=False, header=not os.path.exists("markeringen.csv"))

    df_status.reset_index().to_csv(status_path, index=False)
    st.success("✅ Wijzigingen opgeslagen!")
    st.rerun()

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
