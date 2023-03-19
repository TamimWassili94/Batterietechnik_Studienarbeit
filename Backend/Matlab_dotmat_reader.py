# Diese Datei dient der initialisierung von Matlab Tabellen Dateien.
# In diesem Fall werden die Profile in das Programm eingelesen

"""
scipy.io wird initialisiert um .mat Dateien zu lesen.
pandas wird importiert um die Datei vom scipy format in pandas zu überführen, weil pandas das
Standarttool für Datenanalyse ist"""

import scipy.io
import pandas as pd

# lädt die .mat Datei
def dotmatloader(dateiname):
    scipydata = scipy.io.loadmat(dateiname)
    return scipydata


""" konvertiert die scipydata in ein pandas dataframe. A wurde als Variablenname ergänzt, weil es bei allen 
Batterieprofilen so ist. Empfehlenswert ist hier noch ein selector der eine Variable aussuchen kann"""
def scipytopandasconverter(scipydata):
    dataframe = pd.DataFrame(scipydata['A'])
    dataframe = dataframe.rename(index={0: 'Zeit [s]', 1: 'Leistung [W]'})
    dataframe = dataframe.transpose()
    return dataframe


"""Funktion die alle vorherigen Funktionen als abkürzung ausführt, so dass man nicht mehrere 
Funktionen aufrufen muss, sondern lediglich eine. (Angenehmer beim programmieren)"""
def dotmat_to_pandas(dateiname):
    scipydata = dotmatloader(dateiname)
    return scipytopandasconverter(scipydata)


"""testen der angegebenen Funktionen - erfolgreich"""
#df = dotmat_to_pandas("Profile_1.mat")
#print(df)
#print("Column names:", list(df.columns))
