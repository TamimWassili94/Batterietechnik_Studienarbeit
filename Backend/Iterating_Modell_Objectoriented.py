import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata, interp1d

from Initial_Parameters import q_zelle, soc_init
from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2)

Battery_Dataframe = pd.read_csv('BatteryData_0.csv')

class BatteryModel:
    def __init__(self, initial_voltage, soc_init):
        self.main_voltage = initial_voltage
        self.no_of_cells = 13
        self.ampere = 0
        self.charge = 0
        self.soc = soc_init
        self.ocv = 0
        self.u_r1 = 0
        self.i_r1 = 0
        self.r1 = 0
        self.pre_r1 = 0
        self.c1 = 0
        self.u_r2 = 0
        self.i_r2 = 0
        self.r2 = 0
        self.pre_r2 = 0
        self.c2 = 0
        self.dt = 0.5

        self.main_voltage_list = []  # Anfangswert für Spannung muss gegeben sein
        self.inverted_watt_list = []
        self.main_current_list = []
        self.main_charge_list = []
        self.soc_list = []
        self.ocv_list = []
        self.r_list = []
        self.r1_list = []
        self.c1_list = []
        self.r2_list = []
        self.c2_list = []
        self.u_r_list = []
        self.u_r1_list = []
        self.i_r1_list = []
        self.u_r2_list = []
        self.i_r2_list = []

    def process_row(self, index, row):
        #Schritt 1: Umrechnung von kW in W und thermodynamische richtungsweisung
        watt = self.kilowatt_to_watt_and_reverse(row, 'Leistung [kW]')
        self.inverted_watt_list.append(watt)

        # Schritt 2: Umrechnung von Watt zu Ampere
        if len(self.main_voltage_list) == 0:
            self.ampere = self.watt_to_ampere(watt, self.main_voltage)
            self.main_current_list.append(self.ampere)
        else:
            voltage_to_use = self.main_voltage_list[
                -1]  # or self.main_voltage_list[index] depending on your requirement
            self.ampere = self.watt_to_ampere(watt, voltage_to_use)
            self.main_current_list.append(self.ampere)

        #Schritt 3: Umrechnung von Ampere zu Ladungsmenge (trapezoidal rule)
        self.charge += self.trapezoidal_integration(self.main_current_list, index, self.dt)  # Pass ampere_list to integrate
        self.main_charge_list.append(self.charge)

        #Schritt 4: Berechnung vom SOC:
        self.soc = self.calculating_SOC(self.main_charge_list, index, q_zelle, soc_init)
        self.soc_list.append(self.soc)

        #Schritt 5: Berechnung der komponenten eines Batterieersatzmodells
        self.ocv =  self.lookup_2d(self.soc_list, index, soc_steps_ocv, temp_steps, ocv)
        self.ocv_list.append(self.ocv)

        self.r = self.lookup_2d(self.soc_list, index, SOCsteps, temp_steps, R)
        self.r_list.append(self.r)

        self.r1 = self.lookup_2d(self.soc_list, index, SOCsteps, temp_steps, R1)
        self.r1_list.append(self.r1)

        self.r2 = self.lookup_2d(self.soc_list, index, SOCsteps, temp_steps, R2)
        self.r2_list.append(self.r2)

        self.c1 = self.lookup_2d(self.soc_list, index, SOCsteps, temp_steps, C1)
        self.c1_list.append(self.c1)

        self.c2 = self.lookup_2d(self.soc_list, index, SOCsteps, temp_steps, C2)
        self.c2_list.append(self.c2)

        #Schritt 6: Berechnung von Spannungen und Strömen, bei gegebenen Ohmschen Größen
        self.u_r = self.r * self.ampere
        self.u_r_list.append(self.u_r)

        self.u_r1, self.i_r1, self.pre_r1 = self.simulate_UR_n_and_IR_n_trapezoidal(
            self.r1_list[index], self.main_current_list[index], self.c1_list[index],
            self.u_r1, self.pre_r1, dt=0.5)

        self.u_r2, self.i_r2, self.pre_r2 = self.simulate_UR_n_and_IR_n_trapezoidal(
            self.r2_list[index], self.main_current_list[index], self.c2_list[index],
            self.u_r2, self.pre_r2, dt=0.5)

        # Add the single outputs to your lists
        self.u_r1_list.append(self.u_r1)
        self.i_r1_list.append(self.i_r1)

        self.u_r2_list.append(self.u_r2)
        self.i_r2_list.append(self.i_r2)

        #Schritt 7. Summieren der Spannungen um Spannung zu aktualisieren
        self.main_voltage = (self.ocv + self.u_r + self.u_r1 + self.u_r2) * self.no_of_cells
        self.main_voltage_list.append(self.main_voltage)

    def kilowatt_to_watt_and_reverse(self, row, y_column):
        return row[y_column] * -1000

    def watt_to_ampere(self, kilowatt_value_of_row, voltage_value_of_row):
        return kilowatt_value_of_row / voltage_value_of_row

    def trapezoidal_integration(self, list, index, dt):
        integral = 0.0
        n = len(list)
        if n > 1 and index < n:  # Check if index is in range and you have at least two points
            integral += ((list[index] + list[index - 1]) * dt) / 2
        else:
            integral = 0  # If there is only one point, the integral is zero
        return integral

    def calculating_SOC(self, ladungsmenge_list, index, q_zelle, SOC_init):
        ladung = ladungsmenge_list[index] / q_zelle
        ladung_pro_sekunde = ladung / 3600
        SOC_in_prozent = ladung_pro_sekunde * 100
        SOC = SOC_in_prozent + SOC_init
        if SOC >= 100:
            SOC = 100
        elif SOC <= 0:
            SOC = 0
        return SOC

    def lookup_2d(self, soc_list, index, SOC_breakpoints, Temp_breakpoints, table_data):
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

    def simulate_UR_n_and_IR_n_trapezoidal(self, R1, I_Zelle, C1, initial_output, prev_value3, dt=0.5):
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

    def iterate_model(self, Battery_Dataframe):
        for index, row in Battery_Dataframe.iterrows():
            self.process_row(index, row)

        Battery_Dataframe['Leistung [W]'] = self.inverted_watt_list
        Battery_Dataframe["elektrischer Strom [A]"] = self.main_current_list
        Battery_Dataframe["Ladungsmenge [C]"] = self.main_charge_list
        Battery_Dataframe["SOC [%]"] = self.soc_list
        Battery_Dataframe["OCV [V]"] = self.ocv_list
        Battery_Dataframe["R [Ohm]"] = self.r_list
        Battery_Dataframe["R1 [Ohm]"] = self.r1_list
        Battery_Dataframe["R2 [Ohm]"] = self.r2_list
        Battery_Dataframe["C1 [C]"] = self.c1_list
        Battery_Dataframe["C2 [C]"] = self.c2_list
        Battery_Dataframe["U_R [V]"] = self.u_r_list
        Battery_Dataframe["U_R1 [V]"] = self.u_r1_list
        Battery_Dataframe["U_R2 [V]"] = self.u_r2_list
        Battery_Dataframe["I_R1 [A]"] = self.i_r1_list
        Battery_Dataframe["I_R2 [A]"] = self.i_r2_list
        Battery_Dataframe["U_Ges [V]"] = self.main_voltage_list
        return Battery_Dataframe


battery_model = BatteryModel(45, soc_init)
Battery_Dataframe = battery_model.iterate_model(Battery_Dataframe)


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
    print("Battery_Dataframe columns:", Battery_Dataframe.columns)
    print("Data types in Battery_Dataframe:", Battery_Dataframe.dtypes)
    print("Check for NaN values in DataFrame:", Battery_Dataframe.isna().sum())
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
