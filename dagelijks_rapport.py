import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage
import ssl
import os

# --- INSTELLINGEN ---
CSV_PATH = "strafstatus.csv"
EMAIL_VAN = "leerlingopvolging@gmail.com"              # <-- Vervang dit
EMAIL_NAAR = "brambombaert@spwe.be"             # <-- Vervang dit
APP_WACHTWOORD = "xtjt rvrr uuop cofc"            # <-- Zie stap 2

# --- LADEN DATA ---
vandaag = datetime.now().strftime("%Y-%m-%d")

if not os.path.exists(CSV_PATH):
    print("⚠️ Bestand strafstatus.csv niet gevonden.")
    exit()

df = pd.read_csv(CSV_PATH)

if "laatst_bijgewerkt" not in df.columns or "status" not in df.columns:
    print("⚠️ Kolommen 'laatst_bijgewerkt' of 'status' ontbreken.")
    exit()

# --- FILTER WIJZIGINGEN VAN VANDAAG ---
df_vandaag = df[
    (df["laatst_bijgewerkt"] == vandaag) &
    (df["status"].isin(["wachten_op_straf", "verdubbeld", "strafstudie"]))
]

if df_vandaag.empty:
    print("✅ Geen wijzigingen vandaag.")
    exit()

# --- MAAK RAPPORT ---
regels = []
for _, rij in df_vandaag.iterrows():
    regels.append(f"{rij['naam']} → {rij['status']} op {rij['laatst_bijgewerkt']}")

tekst = "\n".join(regels)

# --- STEL MAIL OP ---
bericht = EmailMessage()
bericht["Subject"] = f"📘 Strafrapport – {vandaag}"
bericht["From"] = EMAIL_VAN
bericht["To"] = EMAIL_NAAR
bericht.set_content(
    f"Hallo,\n\nHier is het automatisch strafrapport van vandaag ({vandaag}):\n\n{tekst}\n\nGroeten,\nDe leerlingenapp"
)

# --- VERSTUUR MAIL ---
context = ssl.create_default_context()
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_VAN, APP_WACHTWOORD)
        smtp.send_message(bericht)
    print("✅ Mail verzonden.")
except Exception as e:
    print(f"❌ Fout bij verzenden: {e}")
