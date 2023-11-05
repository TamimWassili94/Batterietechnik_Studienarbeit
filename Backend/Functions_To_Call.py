import matplotlib.pyplot as plt
from scipy.interpolate import griddata, interp1d, interp2d
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

def integrator(input_aktuell, output_vorher, dt):
    output_aktuell = output_vorher + input_aktuell * dt
    return output_aktuell


def lookup_1d(SOC, SOC_breakpoints, delta_OCV_data):
    # Prüft, ob der Wert innerhalb der Grenzen liegt
    soc_min, soc_max = min(SOC_breakpoints), max(SOC_breakpoints)

    # Wenn SOC innerhalb der Grenzen ist, interpoliert
    if soc_min <= SOC <= soc_max:
        return np.interp(SOC, SOC_breakpoints, delta_OCV_data)

    # Wenn SOC außerhalb der Grenzen ist, Warnung ausgeben
    if SOC < soc_min or SOC > soc_max:
        print(f"Warnung 1D: Der SOC-Wert von {SOC} liegt außerhalb der Grenzen und wird extrapoliert.")

    # Führe die Interpolation (mit Extrapolation für außerhalb der Grenzen liegende Werte) durch
    interpolated_value = np.interp(SOC, SOC_breakpoints, delta_OCV_data)

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



def lookup_2d_v2(SOC, Temp, SOC_breakpoints, Temp_breakpoints, table_data):
    # Create the grid of points for which we have data
    points = np.array([[s, t] for s in SOC_breakpoints for t in Temp_breakpoints])
    values = table_data.flatten()

    # Perform the interpolation
    interpolated_value = griddata(points, values, (SOC, Temp), method='linear')

    if np.isnan(interpolated_value):
        # Create an interpolation function over the grid
        interp_func = interp2d(SOC_breakpoints, Temp_breakpoints, table_data, kind='linear')

        # Perform the interpolation/extrapolation using the function
        # Ensure SOC and Temp are within arrays for interp_func
        interpolated_value = interp_func([SOC], [Temp])

        # Since interp2d returns a 2D array, extract the scalar value
        # Check the dimensions of the output and index accordingly
        if interpolated_value.ndim == 2:
            interpolated_value = interpolated_value[0, 0]
        else:
            # If the result is somehow 1-dimensional, correct the indexing
            interpolated_value = interpolated_value[0]
    # If interpolated_value is not NaN, it's already the correct value

    return interpolated_value


def lookup_2d_v3(SOC, Temp, SOC_breakpoints, Temp_breakpoints, table_data):
    # Erstellt eine Interpolationsfunktion
    interp_func = interp2d(SOC_breakpoints, Temp_breakpoints, table_data, kind='linear')

    # Grid für die Interpolation erstellen
    SOC_grid, Temp_grid = np.meshgrid(SOC_breakpoints, Temp_breakpoints)
    Z = interp_func(SOC_breakpoints, Temp_breakpoints)

    # Plot vorbereiten
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Punktewolke plotten
    ax.scatter(SOC_grid, Temp_grid, Z, color='red', label='Originaldaten')
    ax.set_xlim(SOC_breakpoints.max(), SOC_breakpoints.min())
    # Interpolierte Oberfläche plotten
    # Erstellen Sie ein feineres Grid für die Oberfläche
    SOC_fine = np.linspace(SOC_breakpoints.min(), SOC_breakpoints.max(), 30)
    Temp_fine = np.linspace(Temp_breakpoints.min(), Temp_breakpoints.max(), 30)
    SOC_grid_fine, Temp_grid_fine = np.meshgrid(SOC_fine, Temp_fine)
    Z_fine = interp_func(SOC_fine, Temp_fine)

    # Oberfläche zeichnen
    surf = ax.plot_surface(SOC_grid_fine, Temp_grid_fine, Z_fine, cmap='viridis', alpha=0.7)

    # Achsenbeschriftungen hinzufügen
    ax.set_xlabel('SOC [%]')
    ax.set_ylabel('Temperatur [°C]')
    ax.set_zlabel('Wert')

    # Legende hinzufügen
    ax.legend()

    # Farblegende für die Oberfläche hinzufügen
    fig.colorbar(surf, shrink=0.5, aspect=5, label='Interpolierter Wert')

    plt.show()

    # Werte interpolieren/extrapolieren
    result = interp_func(SOC, Temp)
    return result


def lookup_2d_v4(SOC, Temp, SOC_breakpoints, Temp_breakpoints, table_data):
    # Erstellt die Interpolationsfunktion
    interp_func = interp2d(SOC_breakpoints, Temp_breakpoints, table_data, kind='linear')

    # Prüft, ob die Werte innerhalb der Grenzen liegen
    soc_min, soc_max = min(SOC_breakpoints), max(SOC_breakpoints)
    temp_min, temp_max = min(Temp_breakpoints), max(Temp_breakpoints)

    # Wenn SOC und Temp innerhalb der Grenzen sind, interpoliert
    if soc_min <= SOC <= soc_max and temp_min <= Temp <= temp_max:
        return interp_func(SOC, Temp)[0]

    # Wenn SOC oder Temp außerhalb der Grenzen sind, Warnung ausgeben
    if SOC < soc_min or SOC > soc_max:
        print("\nWarnung 2D: Der SOC-Wert von {} liegt außerhalb der Grenzen und muss extrapoliert werden.".format(Temp))

    if Temp < temp_min or Temp > temp_max:
        print("\nWarnung 2D: Der SOC-Wert von {} liegt außerhalb der Grenzen und muss extrapoliert werden.".format(Temp))
    # Hier kann man eine Extraopolationslogik einfügen
    #     ... Extrapolieren ...
    return interp_func(SOC, Temp)[0]


