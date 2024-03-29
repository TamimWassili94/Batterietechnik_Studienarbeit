import pandas as pd

def read_excel_to_dataframe(file_path, sheet_name=0):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df

# Example usage
R2_Simulink_short = read_excel_to_dataframe('R2_Simulink_cut.xlsx')
R2_Simulink_full = read_excel_to_dataframe('R2_Simulink_full.xlsx')

R2_Simulink_combined = pd.concat([R2_Simulink_short, R2_Simulink_full], axis=1)

R2_short_python = pd.read_csv('R2_Python_short.csv')
R2_short_python.rename(columns={'R2 [Ohm]': 'R2_cut_python [Ohm]'}, inplace=True)

R2_full_python = pd.read_csv('R2_Python_full.csv')
R2_full_python.rename(columns={'R2 [Ohm]': 'R2_full_python [Ohm]'}, inplace=True)

R2_Python_combined = pd.concat([R2_short_python, R2_full_python], axis=1)

R2_full = pd.concat([R2_Python_combined, R2_Simulink_combined], axis =1)


Zeit_sim_cut = R2_Simulink_combined['Zeit_sim_cut [s]']
Zeit_sim_full = R2_Simulink_combined['Zeit_sim [s]']
Zeit_python_cut = R2_Python_combined['Zeit [s]']
Zeit_python_full = R2_Python_combined['Zeit [s]']

R2_sim_cut = R2_Simulink_combined['R2_sim_cut [Ohm]']
R2_sim_full = R2_Simulink_combined['R2_sim_full [Ohm]']
R2_python_cut = R2_Python_combined['R2_cut_python [Ohm]']
R2_python_full = R2_Python_combined['R2_full_python [Ohm]']

R2_error_cut = R2_sim_cut - R2_python_cut
R2_error_full = R2_sim_full - R2_python_full

relative_error_cut = R2_error_cut/ R2_sim_cut
relative_error_full = R2_error_full/ R2_sim_full

percentual_error_cut = relative_error_cut * 100
percentual_error_full = relative_error_full * 100

import matplotlib.pyplot as plt
import numpy as np

# Set the y-axis limits based on your data
ymin1 = -1 # Replace with the minimum value you want to set
ymax1 = 1 # Replace with the maximum value you want to set

ymin = -1.5 # Replace with the minimum value you want to set
ymax = 1.5 # Replace with the maximum value you want to set

# Now you can find the minimum and maximum values
x_min_sim = min(R2_Simulink_short['Zeit_sim_cut [s]'].min(), R2_Simulink_short['Zeit_sim_cut [s]'].max())
x_max_sim = max(R2_Simulink_short['Zeit_sim_cut [s]'].min(), R2_Simulink_short['Zeit_sim_cut [s]'].max())


# Adjust the figure size as needed
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))

# Subplot 1
ax1.plot(Zeit_sim_cut, percentual_error_cut)
ax1.set_title('(a) Prozentualer Fehler - gekürzte Schleife')
ax1.set_xlabel('Zeit [s]')
ax1.set_ylabel('Prozentualer Fehler [%]')
ax1.set_ylim([ymin, ymax])  # Set the y-axis limits
ax1.set_xlim([x_min_sim, x_max_sim])  # Set the x-axis limits
ax1.grid(True)  # Enable grid

# Subplot 2
ax2.plot(Zeit_sim_cut, percentual_error_full)
ax2.set_title('(b) Prozentualer Fehler - Volle Schleife')
ax2.set_xlabel('Zeit [s]')
ax2.set_ylabel('Prozentualer Fehler [%]')
ax2.set_ylim([ymin, ymax])  # Set the y-axis limits
ax2.set_xlim([x_min_sim, x_max_sim])  # Set the x-axis limits
ax2.grid(True)  # Enable grid

# Subplot 3
ax3.plot(Zeit_sim_cut, R2_python_cut, label='R2_python_cut')
ax3.plot(Zeit_sim_cut, R2_sim_cut, label='R2_Simulink_cut')
ax3.set_title('(c) R2 - gekürzte Schleife')
ax3.set_xlabel('Zeit [s]')
ax3.set_ylabel('R2 [Ohm]')
ax3.set_xlim([x_min_sim, x_max_sim])  # Set the x-axis limits
ax3.set_ylim([0.00093, 0.0015])  # Set the y-axis limits
ax3.grid(True)  # Enable grid
ax3.legend()  # Show legend with the defined labels

# Subplot 4
ax4.plot(Zeit_sim_cut, R2_python_full, label='R2_python_full')  # First dataset
ax4.plot(Zeit_sim_full, R2_sim_full, label='R2_Simulink_full')  # Second dataset
ax4.set_title('(c) R2 - Volle Schleife')
ax4.set_xlabel('Zeit [s]')
ax4.set_ylabel('R2 [Ohm]')
ax4.set_xlim([x_min_sim, x_max_sim])  # Set the x-axis limits
ax4.set_ylim([0.00093, 0.0015])  # Set the y-axis limits
ax4.grid(True)  # Enable grid
ax4.legend()  # Show legend with the defined labels

# Adjust layout
plt.tight_layout()

# Show the figure
plt.show()
