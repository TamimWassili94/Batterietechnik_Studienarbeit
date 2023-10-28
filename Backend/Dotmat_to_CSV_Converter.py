import os
import pandas as pd
import scipy.io


def dotmat_to_pandas(dateiname):
    """
    Lädt und konvertiert .mat Datei zu einem Pandas DataFrame.

    Args:
    - dateiname (str): Pfad zur .mat Datei.

    Returns:
    - dataframe (pd.DataFrame): Daten der .mat Datei als Pandas DataFrame.

    Raises:
    - ValueError: Wenn die Dateierweiterung nicht .mat ist.
    """
    # Trennt den Dateinamen von seiner Erweiterung
    _, file_extension = os.path.splitext(dateiname)

    # Überprüft, ob die Dateierweiterung .mat ist
    if file_extension.lower() == ".mat":
        # Lädt die .mat Datei mittels scipy
        scipydata = scipy.io.loadmat(dateiname)

        # Initialisieren des DataFrames mit den Daten aus 'A'
        dataframe = pd.DataFrame(scipydata['A'])

        # Umbenennen der Indexes für bessere Lesbarkeit
        dataframe = dataframe.rename(index={0: 'Zeit [s]', 1: 'Leistung [kW]'})

        # Transponieren des DataFrames, sodass die Spalten und Zeilen vertauscht werden
        dataframe = dataframe.transpose()

        Battery_Dataframe.to_csv('BatteryData_1.csv', index=False)

        print('dataframe wurde erfolgreich initialisiert ung gespeichert')
    else:
        raise ValueError(f"Nicht unterstütztes Dateiformat '{file_extension}'. Bitte stellen Sie einen Pfad für die "
                         f".mat-Datei bereit, um sie zu initialisieren.")

    return dataframe


# testen der angegebenen Funktionen - erfolgreich in klammer dateinamen eingeben des profils
# Das profil muss im gleichen ordner sein wie die .py dateien.
Battery_Dataframe = dotmat_to_pandas("Profile_1.mat")

# .pys arbeiten indem sie das Datafram von .csv ablesen
Battery_Dataframe.to_csv('BatteryData_1.csv', index=False)


