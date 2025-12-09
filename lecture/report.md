# DEUTSCHE BAHN DATENQUALITÄTS-BERICHT

Analyst: Dennis Feyerabend
Datum: 8. Dezember 2025

===================================================================
### PROBLEM 1: Fehlende Werte
===================================================================

KATEGORIE: [Completeness]

BESCHREIBUNG:
Einige Columns haben Null-Werte, obwohl diese nicht erlaubt sind.

BETROFFENE DATEN:
- Spalte: station_name
- Anzahl Zeilen betroffen: 35757 (1.8%)
- Schweregrad: [Niedrig]

BEWEIS (SQL/Code):
- Siehe oben

AUSWIRKUNG:
- Zeilen mit missing values müssen entfernt werden

FIX-STRATEGIE:
- Zeilen entfernen


===================================================================
### PROBLEM 2: Unmögliche Werte
===================================================================

KATEGORIE: [Validity]

BESCHREIBUNG:
- Einige Werte in der Spalte 'delay_in_min' sind unrealistisch niedrig (negativ) oder sehr hoch (849 min - aber noch möglich)

BETROFFENE DATEN:
- Spalte: [delay_in_min]
- Anzahl Zeilen betroffen: 
  - Negative Werte: 46235 (2.33%)
  - Sehr hohe Extremwerte: 1350 (0.07%)
- Schweregrad: [Hoch]

BEWEIS (SQL/Code):
- Siehe oben

AUSWIRKUNG:
- Berechnungen über die Verspätung werden fehlerhaft

FIX-STRATEGIE:
- Entweder negative Verspätungen auf 0 setzen, oder Zeilen entfernen

===================================================================
### PROBLEM 3: Logikfehler
===================================================================

KATEGORIE: [Consistency]

BESCHREIBUNG:
Es gibt Logikfehler in der Spalte 'is_canceled'

BETROFFENE DATEN:
- Spalte: is_canceled
- Anzahl Zeilen betroffen: 1
- Schweregrad: [Niedrig]

BEWEIS (SQL/Code):
- Siehe code oben

AUSWIRKUNG:
- Berechnungen über den Zug delay werden leicht verfälscht da Züge enthalten sind die keine echten Delays hatten

FIX-STRATEGIE:
- Setze Delay auf 0 oder entferne delay komplett

===================================================================
### PROBLEM 4: Outlier
===================================================================

KATEGORIE: [Uniqueness]

BESCHREIBUNG:
- In vielen Kategorischen Columns gibt es eine kleine Anzahl von unique values (eva, train_name, final_destination_station, train_type, train_line_ride_id). 
- Einige der Einträge können valide sein, aber es könnte auch anhand einer falschen Scheibweise liegen

BETROFFENE DATEN:
- Spalte: [eva, train_name, final_destination_station, train_type, train_line_ride_id]
- Anzahl Zeilen betroffen: [Zahl] ([Prozent]% der Daten)
- Schweregrad: [Mittel]

BEWEIS (SQL/Code):
- Siehe Oben

AUSWIRKUNG:
- Zuordnung der Zugparameter klappt nicht mehr zuverlässig

FIX-STRATEGIE:
- Zuerst Schreibweise der Einträge überprüfen und gegenfalls anpassen (uFFFD check)
- Anschließend
  - Entweder alle unique values anzeigen lassen und schauen ob die strings valide sind
  - Oder alle unique values herausfiltern
    - Es gehen realtiv wenig Daten verloren
    - Kategorien mit nur einem Eintrag haben nicht geng datenpunkte um Rückschlüsse zu ermöglichen


===================================================================
### PROBLEM 5: Uniqueness
===================================================================

KATEGORIE: [Uniqueness]

BESCHREIBUNG:
- In vielen Kategorischen Columns gibt es eine kleine Anzahl von unique values (eva, train_name, final_destination_station, train_type, train_line_ride_id). 
- Einige der Einträge können valide sein, aber es könnte auch anhand einer falschen Scheibweise liegen

BETROFFENE DATEN:
- Spalte: [eva, train_name, final_destination_station, train_type, train_line_ride_id]
- Anzahl Zeilen betroffen: [Zahl] ([Prozent]% der Daten)
- Schweregrad: [Mittel]

BEWEIS (SQL/Code):
- Siehe Oben

AUSWIRKUNG:
- Zuordnung der Zugparameter klappt nicht mehr zuverlässig

FIX-STRATEGIE:
- Zuerst Schreibweise der Einträge überprüfen und gegenfalls anpassen (uFFFD check)
- Anschließend
  - Entweder alle unique values anzeigen lassen und schauen ob die strings valide sind
  - Oder alle unique values herausfiltern
    - Es gehen realtiv wenig Daten verloren
    - Kategorien mit nur einem Eintrag haben nicht geng datenpunkte um Rückschlüsse zu ermöglichen


- 