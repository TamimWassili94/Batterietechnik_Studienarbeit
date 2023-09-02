import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import Delaunay
from SOC_Block_in_Python import soc

from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2)



# Für Temp werden gerade konstante Werte angenommen da es noch keine temperatursimulation gibt.
SOC_DATAFRAME = pd.DataFrame({
    'SOC': soc["SOC [%]"],
    'Temp': np.full(2361, 298.15)
})



def plot_lookup_table_with_interpolation(abh_var1, abh_var2, output_werte):
    """
    Erstellt einen 2D-Plot zur Darstellung einer Lookup-Tabelle mit Interpolationslinien.
    """
    # Delaunay-Triangulation
    points = np.array([abh_var1, abh_var2]).T
    tri = Delaunay(points)

    # Erstelle den Plot
    fig, ax = plt.subplots()

    # Zeichne die Triangulation
    ax.triplot(points[:, 0], points[:, 1], tri.simplices, 'g--')
    # Überprüfen, ob die Triangulation erfolgreich ist
    print("Triangulation:", tri.simplices)

    # Scatter Plot der Datenpunkte, die Farbe repräsentiert den Output-Wert
    sc = ax.scatter(abh_var1, abh_var2, c=output_werte, s=100, cmap='viridis', zorder=5)

    # Füge eine Farbleiste hinzu
    plt.colorbar(sc, label='Output-Wert')

    # Achsentitel setzen
    ax.set_xlabel('Abhängige Variable 1')
    ax.set_ylabel('Abhängige Variable 2')

    # Gitternetz anzeigen
    ax.grid(True)

    # Plot anzeigen
    plt.show()

# Ihre Daten
abh_var1 = SOC_DATAFRAME['SOC'].values
abh_var2 = SOC_DATAFRAME['Temp'].values
output_werte = soc_steps_ocv

print(type(abh_var2))
print(type(abh_var1))
print(type(output_werte))

# Aufruf der Funktion
aaa = plot_lookup_table_with_interpolation(abh_var1, abh_var2, output_werte)

x = np.array([0, 1, 2])
y = np.array([0, 1, 0])

plt.scatter(x, y)
plt.show()