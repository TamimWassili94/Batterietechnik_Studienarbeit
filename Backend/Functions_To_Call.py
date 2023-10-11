import matplotlib.pyplot as plt
from scipy.interpolate import griddata, interp1d
import numpy as np

def plot(Dataframe, x_title, y_title):
    # Plotting
    plt.figure()
    plt.plot(Dataframe[x_title], Dataframe[y_title])
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(f'Plot of {y_title}')
    plt.grid(True)
    plt.show()


def lookup_1d(SOC, SOC_breakpoints, delta_OCV_data):
    # Führe die Interpolation für den gegebenen SOC durch
    interpolated_value = np.interp(SOC, SOC_breakpoints, delta_OCV_data)

    # Wenn das Ergebnis NaN ist (obwohl unwahrscheinlich bei 1D-Interpolation), finde den nächsten Wert
    if np.isnan(interpolated_value):
        nearest_SOC_index = np.argmin(np.abs(np.array(SOC_breakpoints) - SOC))
        interpolated_value = delta_OCV_data[nearest_SOC_index]

    return interpolated_value


def lookup_2d(dataframe, SOC_breakpoints, Temp_breakpoints, table_data):
    SOCs = dataframe['SOC [%]'].values  # Liest den Ladungszustand (SOC) aus den Daten
    Temps = dataframe['Temperatur [K]'].values  # Liest die Temperaturen aus den Daten

    # Erstellt ein Gitter für die Datenpunkte
    points = np.array([[t, s] for t in Temp_breakpoints for s in SOC_breakpoints])
    values = table_data.flatten()  # Macht aus der Tabelle eine Liste von Werten

    # Findet Werte für neue Punkte durch Interpolation
    interpolated_values = griddata(points, values, (Temps, SOCs), method='linear')

    # Prüft, ob es Punkte gibt, die nicht interpoliert werden konnten (NaN = Nicht eine Zahl)
    nan_indices = np.isnan(interpolated_values)
    for idx in np.where(nan_indices)[0]:  # Für jeden Punkt, der nicht interpoliert werden konnte
        SOC = SOCs[idx]  # Der aktuelle SOC
        Temp = Temps[idx]  # Die aktuelle Temperatur

        # Findet die nächstgelegenen bekannten Punkte
        nearest_SOC_index = np.argmin(np.abs(np.array(SOC_breakpoints) - SOC))
        nearest_Temp_index = np.argmin(np.abs(np.array(Temp_breakpoints) - Temp))

        # Holt die Datenreihen, die diesen Punkten entsprechen
        SOC_slice = table_data[nearest_Temp_index, :]
        Temp_slice = table_data[:, nearest_SOC_index]

        # Erstellt Funktionen, um Werte für SOC und Temperatur zu schätzen
        f_SOC = interp1d(SOC_breakpoints, SOC_slice, fill_value='extrapolate')
        f_Temp = interp1d(Temp_breakpoints, Temp_slice, fill_value='extrapolate')

        # Schätzt die Werte ab
        SOC_val = f_SOC(SOC)
        Temp_val = f_Temp(Temp)

        # Arithmetischer Mittelwert
        interpolated_values[idx] = (SOC_val + Temp_val) / 2

    # Speichert die interpolierten Werte im dataframe
    dataframe['Interpolated Value'] = interpolated_values
    return dataframe







