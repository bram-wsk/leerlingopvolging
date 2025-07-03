# --- CONTROLEER OP VERDUBBELING ---
nu = datetime.now(ZoneInfo("Europe/Brussels"))  # ✅ Tijdzone-aware huidige tijd
gewijzigd = False
for naam in df_status.index:
    status = df_status.loc[naam, "status"]
    datum_str = df_status.loc[naam, "strafdatum"]

    if status == "wachten_op_straf" and datum_str:
        try:
            strafmoment = datetime.strptime(datum_str, "%d/%m/%Y").replace(tzinfo=ZoneInfo("Europe/Brussels")) + timedelta(hours=16, minutes=15)
            if nu >= strafmoment:
                df_status.loc[naam, "status"] = "verdubbeld"
                # ✅ Voeg automatisch verdubbel_datum toe (morgen)
                df_status.loc[naam, "verdubbel_datum"] = (nu + timedelta(days=1)).strftime("%d/%m/%Y")
                gewijzigd = True
        except ValueError:
            pass

if gewijzigd:
    df_status.reset_index().to_csv(status_path, index=False)
    df_status = herstel_index(df_status)
