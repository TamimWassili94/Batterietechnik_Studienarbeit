import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata, interp1d

from Initial_Parameters import q_zelle, soc_init
from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2)

Battery_Dataframe = pd.read_csv('BatteryData_0.csv')

def kilowatt_to_watt_and_reverse(row,y_column):
    return row[y_column] * -1000

def watt_to_ampere(kilowatt_value_of_row, voltage_value_of_row):
    return kilowatt_value_of_row / voltage_value_of_row

def trapezoidal_integration(list, index, dt):
    integral = 0.0
    n = len(list)
    if n > 1 and index < n:  # Check if index is in range and you have at least two points
        integral += ((list[index] + list[index - 1]) * dt) / 2
    else:
        integral = 0  # If there is only one point, the integral is zero
    return integral


def calculating_SOC(ladungsmenge_list, index, q_zelle, SOC_init):
    ladung = ladungsmenge_list[index]/q_zelle
    ladung_pro_sekunde = ladung / 3600
    SOC_in_prozent = ladung_pro_sekunde * 100
    SOC = SOC_in_prozent + SOC_init
    if SOC >= 100:
        SOC = 100
    elif SOC <= 0:
        SOC = 0
    return SOC

def lookup_2d(soc_list, index , SOC_breakpoints, Temp_breakpoints, table_data):
    SOC = soc_list[index]
    Temp = 298.15
    # Create grid and multivariate data points
    points = np.array([[t, s] for t in Temp_breakpoints for s in SOC_breakpoints])
    values = table_data.flatten()

    # Try to perform interpolation first
    interp_val = griddata(points, values, (Temp, SOC), method='linear')

    # If interp_val is NaN, it means (Temp, SOC) was outside the convex hull of input points
    if np.isnan(interp_val):
        # First, get closest SOC and Temp values
        nearest_SOC_index = np.argmin(np.abs(np.array(SOC_breakpoints) - SOC))
        nearest_Temp_index = np.argmin(np.abs(np.array(Temp_breakpoints) - Temp))

        # Extract relevant rows and columns for 1D interpolation along each axis
        SOC_slice = table_data[nearest_Temp_index, :]
        Temp_slice = table_data[:, nearest_SOC_index]

        # Create 1D interpolation functions for SOC and Temp
        f_SOC = interp1d(SOC_breakpoints, SOC_slice, fill_value='extrapolate')
        f_Temp = interp1d(Temp_breakpoints, Temp_slice, fill_value='extrapolate')

        # Extrapolate
        SOC_val = f_SOC(SOC)
        Temp_val = f_Temp(Temp)

        # Combine the extrapolated values (this is the naive part)
        interp_val = (SOC_val + Temp_val) / 2

    return interp_val

def simulate_UR_n_and_IR_n_trapezoidal(R1, I_Zelle, C1, initial_output, prev_value3, dt=0.5):
    # Step 1: Divide output by R1
    Current = initial_output / R1 if R1 != 0 else 0

    # Step 2: Subtract Value1 from I_Zelle
    Delta_Current = I_Zelle - Current

    # Step 3: Divide Delta_Current by C1
    Value3 = Delta_Current / C1 if C1 != 0 else 0

    # Step 4: Trapezoidal Rule integration to produce new output
    Gradient_of_Voltage = initial_output + (Value3 + prev_value3) * dt / 2

    # Save new output for the next iteration
    initial_output = Gradient_of_Voltage
    prev_value3 = Value3

    return initial_output, Current, prev_value3

def iterating_battery_modell(Battery_Dataframe, initial_voltage, soc_init):
    U_1 = initial_voltage
    U_list = []
    anzahl_an_zellen = 13
    watt_and_reverse_list = []
    ampere_list = []
    voltage_list = [] # Anfangswert für Spannung muss gegeben sein
    Ladungsmenge_list = []
    Ladungsmenge = 0
    SOC_list = []

    Open_Circuit_Voltage_list = []
    Resistor_list = []
    Resistor1_list = []
    Capacitor1_list = []
    Resistor2_list = []
    Capacitor2_list = []

    U_R_list = []

    U_R1_list = []
    I_R1_list = []
    U_R1 = 0
    prev_value_R1 = 0

    U_R2_list = []
    I_R2_list = []
    U_R2 = 0
    prev_value_R2 = 0
    dt = 0.5

    for index, row in Battery_Dataframe.iterrows():
        #Schritt 1: Umrechnung von kW in W und thermodynamische richtungsweisung
        watt = kilowatt_to_watt_and_reverse(row, 'Leistung [kW]')
        watt_and_reverse_list.append(watt)

        #Schritt 2: Umrechnung von Watt zu Ampere
        if len(voltage_list) == 0:
            ampere = watt_to_ampere(watt, U_1)
            ampere_list.append(ampere)
        else:
            ampere = watt_to_ampere(kilowatt_to_watt_and_reverse(watt, voltage_list[index]))
            ampere_list.append(ampere)

        #Schritt 3: Umrechnung von Ampere zu Ladungsmenge (trapezoidal rule)
        Ladungsmenge += trapezoidal_integration(ampere_list, index, dt)  # Pass ampere_list to integrate
        Ladungsmenge_list.append(Ladungsmenge)

        #Schritt 4: Berechnung vom SOC:
        SOC = calculating_SOC(Ladungsmenge_list, index, q_zelle, soc_init)
        SOC_list.append(SOC)

        #Schritt 5: Berechnung der komponenten eines Batterieersatzmodells
        Open_Circuit_Voltage =  lookup_2d(SOC_list, index, soc_steps_ocv, temp_steps, ocv)
        Open_Circuit_Voltage_list.append(Open_Circuit_Voltage)

        Resistor = lookup_2d(SOC_list, index, SOCsteps, temp_steps, R)
        Resistor_list.append(Resistor)

        Resistor1 = lookup_2d(SOC_list, index, SOCsteps, temp_steps, R1)
        Resistor1_list.append(Resistor1)

        Resistor2 = lookup_2d(SOC_list, index, SOCsteps, temp_steps, R2)
        Resistor2_list.append(Resistor2)

        Capacitor1 = lookup_2d(SOC_list, index, SOCsteps, temp_steps, C1)
        Capacitor1_list.append(Capacitor1)

        Capacitor2 = lookup_2d(SOC_list, index, SOCsteps, temp_steps, C2)
        Capacitor2_list.append(Capacitor2)

        #Schritt 6: Berechnung von Spannungen und Strömen, bei gegebenen Ohmschen Größen
        U_R = Resistor * ampere
        U_R_list.append(U_R)

        U_R1, Current_R1, prev_value_R1 = simulate_UR_n_and_IR_n_trapezoidal(
            Resistor1_list[index], ampere_list[index], Capacitor1_list[index],
            U_R1, prev_value_R1, dt=0.5)

        U_R2, Current_R2, prev_value_R2 = simulate_UR_n_and_IR_n_trapezoidal(
            Resistor2_list[index], ampere_list[index], Capacitor2_list[index],
            U_R2, prev_value_R2, dt=0.5)

        # Add the single outputs to your lists
        U_R1_list.append(U_R1)
        I_R1_list.append(Current_R1)

        U_R2_list.append(U_R2)
        I_R2_list.append(Current_R2)

        #Schritt 7. Summieren der Spannungen um Spannung zu aktualisieren
        U_1 = (Open_Circuit_Voltage + U_R + U_R1 + U_R2) * anzahl_an_zellen
        U_list.append(U_1)


    Battery_Dataframe['Leistung [W]'] = watt_and_reverse_list
    Battery_Dataframe["elektrischer Strom [A]"] = ampere_list
    Battery_Dataframe["Ladungsmenge [C]"] = Ladungsmenge_list
    Battery_Dataframe["SOC [%]"] = SOC_list
    Battery_Dataframe["OCV [V]"] = Open_Circuit_Voltage_list
    Battery_Dataframe["R [Ohm]"] = Resistor_list
    Battery_Dataframe["R1 [Ohm]"] = Resistor1_list
    Battery_Dataframe["R2 [Ohm]"] = Resistor2_list
    Battery_Dataframe["C1 [C]"] = Capacitor1_list
    Battery_Dataframe["C2 [C]"] = Capacitor2_list
    Battery_Dataframe["U_R [V]"] = U_R_list
    Battery_Dataframe["U_R1 [V]"] = U_R1_list
    Battery_Dataframe["U_R2 [V]"] = U_R2_list
    Battery_Dataframe["I_R1 [A]"] = I_R1_list
    Battery_Dataframe["I_R2 [A]"] = I_R2_list
    Battery_Dataframe["U_Ges [V]"] = U_list
    return Battery_Dataframe

Battery_Dataframe = iterating_battery_modell(Battery_Dataframe, 45, soc_init)


def plot(Dataframe, x_title, y_title):
    # Plotting
    plt.figure()
    plt.plot(Dataframe[x_title], Dataframe[y_title])
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(f'Plot of {y_title}')
    plt.grid(True)
    plt.show()

def plot_2_elements(x_axis, y_axis1, y_axis2, title, unit):
    # Create the first plot and store the axis object
    ax = Battery_Dataframe.plot(x=x_axis, y=y_axis1, label=y_axis1)

    # Use the same axis object for the second plot
    Battery_Dataframe.plot(x=x_axis, y=y_axis2, ax=ax, label=y_axis2)

    # Customize the plot
    plt.xlabel(x_axis)
    plt.ylabel(f'{title} {unit}')
    plt.title(f'{title} over Time - Trapezoid')
    ax.grid(True)  # This line adds grid lines

    ax.legend()
    plt.show()

plot(Battery_Dataframe, "Zeit [s]", 'Leistung [W]')
plot(Battery_Dataframe, "Zeit [s]", "elektrischer Strom [A]")
plot(Battery_Dataframe, "Zeit [s]", "Ladungsmenge [C]")
plot(Battery_Dataframe, "Zeit [s]", "SOC [%]")
plot(Battery_Dataframe, "Zeit [s]", "OCV [V]")
plot(Battery_Dataframe, "Zeit [s]", "R [Ohm]")
plot(Battery_Dataframe, "Zeit [s]", "R1 [Ohm]")
plot(Battery_Dataframe, "Zeit [s]", "R2 [Ohm]")
plot(Battery_Dataframe, "Zeit [s]", "C1 [C]")
plot(Battery_Dataframe, "Zeit [s]", "C2 [C]")
plot(Battery_Dataframe, "Zeit [s]", "U_R1 [V]")
plot_2_elements('Zeit [s]', 'U_R1 [V]', 'U_R2 [V]', 'Voltage', '[V]')
plot_2_elements('Zeit [s]', 'I_R1 [A]', 'I_R2 [A]', 'Ampere', '[A]')
plot(Battery_Dataframe, "Zeit [s]", "U_Ges [V]")
