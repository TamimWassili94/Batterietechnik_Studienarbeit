import pandas as pd

R2_full_python = pd.read_csv('Gesamtspannung_Python_full.csv')
R2_full_python = R2_full_python.iloc[34:48]

Zeit_python_cut = R2_full_python['Zeit [s]']
U_ges_full = R2_full_python['U_Batterie [V]']

import matplotlib.pyplot as plt
plt.plot(Zeit_python_cut, U_ges_full)
plt.xlabel('Zeit [s]')
plt.ylabel('U_ges_python [V]')
plt.title('Rückführung U_Batterie [V] für nächste Iteration - Python')
plt.ylim([46.4, 47.12])  # Set the y-axis limits
plt.grid(True)  # Enable grid
plt.show()

