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

    with col3:
        status = df_status.loc[df_status["naam"] == naam, "status"].values[0]
        
        # Zet status als er 3 strepen zijn en nog geen status
        if strepen == 3 and status != "wachten_op_straf":
            df_status.loc[df_status["naam"] == naam, "status"] = "wachten_op_straf"
            status = "wachten_op_straf"

        # Toon status en knop om te verwijderen
        if status == "wachten_op_straf":
            col3.markdown("🟠 *Wachten op straf*")
            if col3.button("Straf afgehandeld", key=f"straf_af_{i}"):
                df_status.loc[df_status["naam"] == naam, "status"] = ""
                st.success(f"✅ Strafstatus verwijderd voor {naam}")
                df_status.to_csv(status_path, index=False)
                st.rerun()  # <-- aangepast

    # Voeg markeringen toe aan invoer
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

        # Strafstatus blijft behouden
        df_status.to_csv(status_path, index=False)

        st.rerun()  # <-- aangepast
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
