import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

Battery_Dataframe_partial = pd.read_csv('Battery_Dataframe_partial_charge.csv')
Battery_Dataframe_full = pd.read_csv('Battery_Dataframe_full_charge.csv')

Ladung_Dataframe0 = pd.read_csv('Charge_Simulink.csv')
Ladung_Dataframe1 = pd.read_csv('Charge_Simulink_full.csv')

Time = Battery_Dataframe_partial['Zeit [s]']
Ladung_Dataframe_Simulink0 = Ladung_Dataframe0['Charge']
Ladung_Dataframe_Python0 = Battery_Dataframe_partial['Charge [C]']
error_partial = Ladung_Dataframe_Simulink0 - Ladung_Dataframe_Python0

combined_dataframe_partial = pd.concat([Ladung_Dataframe_Simulink0, Ladung_Dataframe_Python0], axis=1)
combined_dataframe_partial['Zeit [s]'] = Time
combined_dataframe_partial.columns = ['Ladung_Simulink [F]', 'Ladung_Python [F]', 'Zeit [s]']
combined_dataframe_partial['error'] = combined_dataframe_partial['Ladung_Simulink [F]'] - combined_dataframe_partial['Ladung_Python [F]']
combined_dataframe_partial['relative_error'] = (combined_dataframe_partial['Ladung_Simulink [F]'] - combined_dataframe_partial['Ladung_Python [F]']) / combined_dataframe_partial['Ladung_Simulink [F]']
combined_dataframe_partial['prozentualer Fehlerverlauf [%]'] = 100 * (combined_dataframe_partial['Ladung_Simulink [F]'] - combined_dataframe_partial['Ladung_Python [F]']) / combined_dataframe_partial['Ladung_Simulink [F]']
combined_dataframe_partial['Zeit [s]'] = Battery_Dataframe_partial ["Zeit [s]"]

Time = Battery_Dataframe_full['Zeit [s]']
Ladung_Dataframe_Simulink1 = Ladung_Dataframe1['Charge']
Ladung_Dataframe_Python1 = Battery_Dataframe_full['Charge [C]']
error_partial = Ladung_Dataframe_Simulink1 - Ladung_Dataframe_Python1

combined_dataframe1 = pd.concat([Ladung_Dataframe_Simulink1, Ladung_Dataframe_Python1], axis=1)
Time_full = Battery_Dataframe_full['Zeit [s]']  # Use the correct Time for the full dataframe
combined_dataframe1['Zeit [s]'] = Time_full
combined_dataframe1.columns = ['Ladung_Simulink [F]', 'Ladung_Python [F]', 'Zeit [s]']
combined_dataframe1['error'] = combined_dataframe1['Ladung_Simulink [F]'] - combined_dataframe1['Ladung_Python [F]']
combined_dataframe1['relative_error'] = (combined_dataframe1['Ladung_Simulink [F]'] - combined_dataframe1['Ladung_Python [F]']) / combined_dataframe1['Ladung_Simulink [F]']
combined_dataframe1['prozentualer Fehlerverlauf [%]'] = 100 * (combined_dataframe1['Ladung_Simulink [F]'] - combined_dataframe1['Ladung_Python [F]']) / combined_dataframe1['Ladung_Simulink [F]']
combined_dataframe1['Zeit [s]'] = Battery_Dataframe_full ["Zeit [s]"]

# Assuming 'combined_dataframe_partial' and 'combined_dataframe1' are already defined and have the correct data.

abs_max_error = max(combined_dataframe_partial['prozentualer Fehlerverlauf [%]'].abs().max(),
                    combined_dataframe1['prozentualer Fehlerverlauf [%]'].abs().max())

abs_max_error += 0.2 * abs_max_error

min_time = min(combined_dataframe_partial['Zeit [s]'].min(), combined_dataframe1['Zeit [s]'].min())
max_time = max(combined_dataframe_partial['Zeit [s]'].max(), combined_dataframe1['Zeit [s]'].max())


fig, axs = plt.subplots(2, 2, figsize=(10, 8))  # Creates a 2x2 grid of subplots
plt.rcParams.update({'font.size': 11})
axs[0, 0].set_xlim([min_time, max_time])
axs[0, 1].set_xlim([min_time, max_time])
axs[1, 0].set_xlim([min_time, max_time])
axs[1, 1].set_xlim([min_time, max_time])



# Für den oberen linken Plot
axs[0, 0].grid(True)
axs[0, 1].grid(True)
axs[1, 0].grid(True)  # Aktiviert das Gitter
axs[1, 1].grid(True)  # Aktiviert das Gitter


# Top left plot for 'prozentualer Fehlerverlauf [%]' from partial dataframe
axs[0, 0].set_ylim([-abs_max_error, abs_max_error])
axs[0, 0].plot(combined_dataframe_partial['Zeit [s]'], combined_dataframe_partial['prozentualer Fehlerverlauf [%]'])
axs[0, 0].set_title('(a) Prozentualer Fehler - gekürzte Schleife')
axs[0, 0].set_xlabel('Zeit [s]',fontsize='11')
axs[0, 0].set_ylabel('Prozentualer Fehler [%]',fontsize='11')

# Top right plot for 'prozentualer Fehlerverlauf [%]' from full dataframe
axs[0, 1].set_ylim([-abs_max_error, abs_max_error])
axs[0, 1].plot(combined_dataframe1['Zeit [s]'], combined_dataframe1['prozentualer Fehlerverlauf [%]'])
axs[0, 1].set_title('(b) Prozentualer Fehler - Volle Schleife')
axs[0, 1].set_xlabel('Zeit [s]',fontsize='11')
axs[0, 1].set_ylabel('Prozentualer Fehler [%]',fontsize='11')


# Bottom left plot for 'Ladung_Simulink [F]' and 'Ladung_Python [F]' from partial dataframe
axs[1, 0].plot(combined_dataframe_partial['Zeit [s]'], combined_dataframe_partial['Ladung_Simulink [F]'], label='Ladung_Simulink - Partial')
axs[1, 0].plot(combined_dataframe_partial['Zeit [s]'], combined_dataframe_partial['Ladung_Python [F]'], label='Ladung_Python - Partial')
axs[1, 0].set_title('(c) Ladung - gekürzte Schleife')
axs[1, 0].set_xlabel('Zeit [s]',fontsize='11')
axs[1, 0].set_ylabel('Ladung [C]',fontsize='11')
axs[1, 0].legend()

# Bottom right plot for 'Ladung_Simulink [F]' and 'Ladung_Python [F]' from full dataframe
axs[1, 1].plot(combined_dataframe1['Zeit [s]'], combined_dataframe1['Ladung_Simulink [F]'], label='Ladung_Simulink - Full')
axs[1, 1].plot(combined_dataframe1['Zeit [s]'], combined_dataframe1['Ladung_Python [F]'], label='Ladung_Python - Full')
axs[1, 1].set_title('(d) Ladung - Volle Schleife')
axs[1, 1].set_xlabel('Zeit [s]',fontsize='11')
axs[1, 1].set_ylabel('Ladung [C]',fontsize='11')
axs[1, 1].legend()


axs[1, 0].legend(fontsize='11')
axs[1, 1].legend(fontsize='11')

# Adjust layout to prevent overlapping
plt.tight_layout()

# Show the plot
plt.show()
