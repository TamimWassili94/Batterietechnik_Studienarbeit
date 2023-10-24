import pandas as pd

# Dataframe mit bereits gegebenen Zeitstempeln
df = pd.DataFrame({'Zeit': [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]})

# Erzeugen einer Spalte gefüllt mit dem Initialwert
initialwert = 0
df['Wert'] = initialwert    #[0, 0, 0, 0, 0, 0]

# Der Wert, der für die erste Berechnung verwendet wird, ist der Initialwert
aktueller_wert = initialwert

# Schleife durch jeden Zeitpunkt im Beispiel DataFrame ab index = 1
for index, row in df.iloc[1:].iterrows():
    # Der vorherige Wert wird der aktuelle Wert für diese Iteration
    vorheriger_wert = aktueller_wert

    # Addieret den vorherigen Wert zum aktuellen Wert
    aktueller_wert += vorheriger_wert

    # Aktualisiert den Wert im DataFrame
    df.at[index, 'Wert'] = aktueller_wert

