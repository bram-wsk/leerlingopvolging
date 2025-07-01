import pandas as pd
from datetime import datetime
import os

# Vervang dit met jouw Google Sheet ID
SHEET_ID = "1AbCDeFgHiJkLmNoPqRsTuVwXyZ1234567890"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Bestandsnaam waar alles wordt opgeslagen
OUTPUT_BESTAND = "markeringen.csv"

def lees_leerlingen(sheet_url):
    try:
        df = pd.read_csv(sheet_url)
        if "naam" not in df.columns:
            raise ValueError("❌ Kolom 'naam' ontbreekt in de sheet.")
        return df
    except Exception as e:
        print(f"❌ Fout bij inlezen van leerlingen: {e}")
        exit()

def selecteer_leerling(leerlingen_df):
    print("\n📋 Leerlingenlijst:\n")
    for i, naam in enumerate(leerlingen_df["naam"], start=1):
        print(f"{i}. {naam}")
    try:
        keuze = int(input("\nNummer van leerling: "))
        return leerlingen_df.iloc[keuze - 1]["naam"]
    except:
        print("❌ Ongeldige keuze.")
        exit()

def voeg_markering_toe(naam, bestand):
    reden = input("Reden van markering: ").strip()
    streep = input("Aantal strepen (bv. 1): ").strip()
    datum = datetime.today().strftime("%Y-%m-%d")

    regel = {
        "datum": datum,
        "naam": naam,
        "reden": reden,
        "strepen": streep
    }

    df_nieuw = pd.DataFrame([regel])

    bestand_bestaat = os.path.isfile(bestand)
    df_nieuw.to_csv(bestand, mode="a", index=False, header=not bestand_bestaat)
    print(f"✅ Markering opgeslagen in '{bestand}'.")

def main():
    leerlingen = lees_leerlingen(SHEET_URL)
    naam = selecteer_leerling(leerlingen)
    voeg_markering_toe(naam, OUTPUT_BESTAND)

if __name__ == "__main__":
    main()

