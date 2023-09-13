import pandas as pd
import matplotlib.pyplot as plt

from Initial_Parameters import q_zelle, soc_init
Battery_Dataframe = pd.read_csv('BatteryData_0.csv')

def kilowatt_to_watt_and_reverse(row,y_column):
    return row[y_column] * -1000

def watt_to_ampere(kilowatt_value_of_row, voltage_value_of_row):
    return kilowatt_value_of_row / voltage_value_of_row


def trapezoidal_integration(y_values, dt):
    integral = 0.0
    n = len(y_values)

    for i in range(1, n):
        integral += (y_values[i] + y_values[i - 1]) * dt / 2.0

    return integral

def iterating_battery_modell(Battery_Dataframe, initial_voltage):
    watt_and_reverse_list = []
    ampere_list = []
    voltage_list = [] # Anfangswert für Spannung muss gegeben sein
    Ladungsmenge_list = []

    dt = 0.5

    for index, row in Battery_Dataframe.iterrows():
        #Schritt 1: Umrechnung von kW in W und thermodynamische richtungsweisung
        watt = kilowatt_to_watt_and_reverse(row, 'Leistung [kW]')
        watt_and_reverse_list.append(watt)

        #Schritt 2: Umrechnung von Watt zu Ampere
        if len(voltage_list) == 0:
            ampere = watt_to_ampere(watt, initial_voltage)
            ampere_list.append(ampere)
        else:
            ampere = watt_to_ampere(kilowatt_to_watt_and_reverse(watt, voltage_list[index]))
            ampere_list.append(ampere)

        #Schritt 3: Umrechnung von Ampere zu Ladungsmenge (trapezoidal rule)
        if len(ampere_list) > 1:  # You need at least two points to integrate
            Ladungsmenge = trapezoidal_integration(ampere_list, dt)
            Ladungsmenge_list.append(Ladungsmenge)
        else:
            Ladungsmenge = 0  # If there is only one point, the integral is zero
            Ladungsmenge_list.append(Ladungsmenge)

    Battery_Dataframe["Strom"] = ampere_list
    Battery_Dataframe["Ladungsmenge"] = Ladungsmenge_list
    return Battery_Dataframe

Battery_Dataframe = iterating_battery_modell(Battery_Dataframe, 45)
# Plotting
plt.figure()
plt.plot(Battery_Dataframe['Ladungsmenge'])
plt.xlabel('Index')
plt.ylabel('your_column_name')
plt.title('Plot of your_column_name')
plt.grid(True)
plt.show()


