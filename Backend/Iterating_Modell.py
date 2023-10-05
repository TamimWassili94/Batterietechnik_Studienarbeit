import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata, interp1d

from Initial_Parameters import q_zelle, Temperature
from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2, DeltaOCVdT, SOCsteps_Takano,
                                kA, cp, m)

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

def lookup_2d(temperature, soc_list, index, SOC_breakpoints, Temp_breakpoints, table_data):
    SOC = soc_list[index]
    Temp = temperature
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


def lookup_1d(soc_list, index):
    SOC = soc_list[index]

    # Try to perform interpolation first
    try:
        interp_val = np.interp(SOC, SOCsteps_Takano, DeltaOCVdT)
    except ValueError:
        # If SOC is outside the range, extrapolate using nearest endpoints
        if SOC < SOCsteps_Takano[0]:
            slope = (DeltaOCVdT[1] - DeltaOCVdT[0]) / (SOCsteps_Takano[1] - SOCsteps_Takano[0])
            interp_val = DeltaOCVdT[0] + slope * (SOC - SOCsteps_Takano[0])
        else:
            slope = (DeltaOCVdT[-1] - DeltaOCVdT[-2]) / (SOCsteps_Takano[-1] - SOCsteps_Takano[-2])
            interp_val = DeltaOCVdT[-1] + slope * (SOC - SOCsteps_Takano[-1])

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

def calculate_irreversible_heat(Resistor, Resistor_1,Resistor_2, I_R, I_R1, I_R2):
    q_irr_resistor = Resistor * I_R**2
    q_irr_resistor_1 = Resistor_1 * I_R1**2
    q_irr_resistor_2 = Resistor_2 * I_R2**2
    return q_irr_resistor_1 + q_irr_resistor + q_irr_resistor_2

def calculate_total_heat(Q_irr, Q_rev):
    Q_rev_total = Q_rev * 13
    Q_irr_total = Q_irr * 13
    Q_total = Q_rev_total + Q_irr_total
    Q_cell = Q_total / 13
    return Q_total, Q_cell


def calculate_temperature(init_temp, heat_transfer_list, temp_list, q_cell, index, dt=0.5):
    # For the unit delay, if index is 0 (or if the list is empty), use init_temp. Otherwise, use the last value in temp_list.
    unit_delay = init_temp if index == 0 or not temp_list else temp_list[-1]

    # Difference Block
    delta_temp = init_temp - unit_delay

    # Gain kA
    a = delta_temp * kA

    # Sum Block
    b = a + q_cell

    # Division to get c
    c = b / (m * cp)

    # Integrator Block - Simple Euler Integration
    new_temp = unit_delay + c * dt

    temp_list.append(new_temp)

    return temp_list, heat_transfer_list


def iterating_battery_modell(Battery_Dataframe, initial_voltage, soc_init, initial_temperature):
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

    Q_irr_list = []
    Q_rev_list = []

    Q_total_list = []
    Q_cell_list = []

    heat_transfer_list = []

    temp = initial_temperature
    temp_list = []

    for index, row in Battery_Dataframe.iterrows():
        ## Berechnung der elektrischen Größen
        #Schritt 1: Umrechnung von kW in W und thermodynamische richtungsweisung
        watt = kilowatt_to_watt_and_reverse(row, 'Leistung [kW]')
        watt_and_reverse_list.append(watt)

        #Schritt 2: Umrechnung von Watt zu Ampere
        if len(voltage_list) == 0:
            main_current = watt_to_ampere(watt, U_1)
            ampere_list.append(main_current)
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
        Open_Circuit_Voltage =  lookup_2d(temp, SOC_list, index, soc_steps_ocv, temp_steps, ocv)
        Open_Circuit_Voltage_list.append(Open_Circuit_Voltage)

        Resistor = lookup_2d(temp, SOC_list, index, SOCsteps, temp_steps, R)
        Resistor_list.append(Resistor)

        Resistor1 = lookup_2d(temp, SOC_list, index, SOCsteps, temp_steps, R1)
        Resistor1_list.append(Resistor1)

        Resistor2 = lookup_2d(temp, SOC_list, index, SOCsteps, temp_steps, R2)
        Resistor2_list.append(Resistor2)

        Capacitor1 = lookup_2d(temp, SOC_list, index, SOCsteps, temp_steps, C1)
        Capacitor1_list.append(Capacitor1)

        Capacitor2 = lookup_2d(temp, SOC_list, index, SOCsteps, temp_steps, C2)
        Capacitor2_list.append(Capacitor2)

        #Schritt 6: Berechnung von Spannungen und Strömen, bei gegebenen Ohmschen Größen
        U_R = Resistor * main_current
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


        ## Berechnung der Wärmegrößen
        #Schritt 1. Berechnung von Q_irr
        Q_irr = calculate_irreversible_heat(Resistor, Resistor1, Resistor2, main_current, Current_R1, Current_R2)
        Q_irr_list.append(Q_irr)

        #Schritt 2. Berechnung von Q_rev
        SOC_Takano_rev = lookup_1d(SOC_list, index)
        Q_rev = SOC_Takano_rev * temp * main_current
        Q_rev_list.append(Q_rev)

        #Schritt 3. Berechnung der totalen Wärme und der Wärme pro Zelle
        Q_total, Q_cell = calculate_total_heat(Q_irr, Q_rev)
        Q_total_list.append(Q_total)
        Q_cell_list.append(Q_cell)

        #Schritt 4. Berechnung der Temperatur
        temp_list, heat_transfer_list = calculate_temperature(
            initial_temperature ,heat_transfer_list, temp_list, Q_cell, index
        )
        temp = initial_temperature

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
    Battery_Dataframe["Q_irr [W]"] = Q_irr_list
    Battery_Dataframe["Q_rev [W]"] = Q_rev_list
    Battery_Dataframe["Q_total [W]"] = Q_total_list
    Battery_Dataframe["Q_cell [W]"] = Q_cell_list
    Battery_Dataframe["Temp [K]"] = temp_list
    return Battery_Dataframe

Battery_Dataframe = iterating_battery_modell(Battery_Dataframe, 45, 60, Temperature)


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
plot(Battery_Dataframe, "Zeit [s]", "Q_irr [W]")
plot(Battery_Dataframe, "Zeit [s]", "Q_rev [W]")
plot(Battery_Dataframe, "Zeit [s]", "Q_cell [W]")
plot(Battery_Dataframe, "Zeit [s]", "Temp [K]")