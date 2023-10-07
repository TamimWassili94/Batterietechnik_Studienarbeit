import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata, interp1d
from scipy.integrate import odeint

from Initial_Parameters import q_zelle, Temperature, soc_init
from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2, DeltaOCVdT, SOCsteps_Takano,
                                kA, cp, m)


Battery_Dataframe = pd.read_csv('BatteryData_0.csv')

def plot(Dataframe, x_title, y_title):
    # Plotting
    plt.figure()
    plt.plot(Dataframe[x_title], Dataframe[y_title])
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(f'Plot of {y_title}')
    plt.grid(True)
    plt.show()


def integrate_dataframe(df, input_column, time_column, output_column):
    """
    Integriert das Eingangssignal über die Zeit.

    :param df: Das DataFrame mit den Daten.
    :param input_column: Der Name der Spalte mit dem Eingangssignal.
    :param time_column: Der Name der Spalte mit den Zeitwerten.
    :param output_column: Der Name der Spalte, in der das integrierte Signal gespeichert wird.
    """
    df[output_column] = (df[input_column] * df[time_column].diff().fillna(0)).cumsum()



def fast_lookup_2d(dataframe, SOC_breakpoints, Temp_breakpoints, table_data):
    SOCs = dataframe['SOC [%]'].values
    Temps = dataframe['Temperatur [K]'].values

    # Create grid and multivariate data points
    points = np.array([[t, s] for t in Temp_breakpoints for s in SOC_breakpoints])
    values = table_data.flatten()

    # Perform interpolation for all points
    interpolated_values = griddata(points, values, (Temps, SOCs), method='linear')

    # Handle NaN values (where (Temp, SOC) was outside the convex hull of input points)
    nan_indices = np.isnan(interpolated_values)
    for idx in np.where(nan_indices)[0]:
        SOC = SOCs[idx]
        Temp = Temps[idx]

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

        # Combine the extrapolated values
        interpolated_values[idx] = (SOC_val + Temp_val) / 2

    dataframe['Interpolated Value'] = interpolated_values
    return dataframe



# Time steps (assuming uniform time step from the dataframe's index)
t = Battery_Dataframe["Zeit [s]"].values
init_volt = 3.6*13


#Schritt 1 - Kilowatt zu Watt in thermodynamisch richtiger Richtung
Battery_Dataframe['Leistung [W]'] = Battery_Dataframe['Leistung [kW]'] * -1000

#Schritt 2 - Watt zu Ampere durch Division mit der Spannung
Battery_Dataframe['Current [A]'] = Battery_Dataframe['Leistung [W]'] / init_volt

#Schritt 3 - Berechnung von Ampere zu Ladung
integrate_dataframe(Battery_Dataframe, 'Current [A]', 'Zeit [s]', 'Charge [C]')

#Schritt 4 - Berechnung von Ladung zu SOC
denumerator_qzelle = 1/q_zelle
stunden_zu_sekunde = 1/3600
prozent = 100
Battery_Dataframe['SOC [%]'] = Battery_Dataframe['Charge [C]'] * denumerator_qzelle * stunden_zu_sekunde * prozent
Battery_Dataframe['SOC [%]'] = Battery_Dataframe['SOC [%]'] + soc_init
Battery_Dataframe['SOC [%]'] = Battery_Dataframe['SOC [%]'].clip(0, 100)  # Beschränkt die Werte auf den Bereich [0, 100]

#Schritt 5 - Berechnung von Ohmschen Größen
Battery_Dataframe['Temperatur [K]'] = Temperature
##Schritt 5.1 - Berechnung vom OCV
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, soc_steps_ocv, temp_steps, ocv)
Battery_Dataframe.rename(columns={'Interpolated Value': 'OCV [V]'}, inplace=True)

##Schritt 5.2 - Berechnung von R
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, R)
Battery_Dataframe.rename(columns={'Interpolated Value': 'R [Ohm]'}, inplace=True)

##Schritt 5.3 - Berechnung von R1
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, R1)
Battery_Dataframe.rename(columns={'Interpolated Value': 'R1 [Ohm]'}, inplace=True)

##Schritt 5.4 - Berechnung von R2
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, R2)
Battery_Dataframe.rename(columns={'Interpolated Value': 'R2 [Ohm]'}, inplace=True)

##Schritt 5.5 - Berechnung von C1
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, C1)
Battery_Dataframe.rename(columns={'Interpolated Value': 'C1 [Ohm]'}, inplace=True)

##Schritt 5.6 - Berechnung von C2
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, C2)
Battery_Dataframe.rename(columns={'Interpolated Value': 'C2 [Ohm]'}, inplace=True)

#Schritt 6 - Berechnung der Spannungen aus den Ohmschen Größen
##Schritt 6.1 - Berechnung der Spannung U_R
Battery_Dataframe["U_R [V]"] = Battery_Dataframe['R [Ohm]'] * Battery_Dataframe['Current [A]']

#Schritt 7 - Simulation for U_R1 [V] and I_R1 [A]
# Initialize an array for storing U_R1 values with the initial condition
U_R1_out = np.zeros_like(Battery_Dataframe["Zeit [s]"].values)

for i in range(1, len(t)):
    tspan = [t[i-1], t[i]]
    R1, Current, C1 = Battery_Dataframe['R1 [Ohm]'].values[i], Battery_Dataframe['Current [A]'].values[i], Battery_Dataframe['C1 [Ohm]'].values[i]
    U_R1 = odeint(lambda U_R1, t: (Current - U_R1 / R1) / C1, U_R1_out[i-1], tspan)[-1]
    U_R1_out[i] = U_R1[0]

Battery_Dataframe['U_R1 [V]'] = U_R1_out
Battery_Dataframe['I_1 [A]'] = (Battery_Dataframe['U_R1 [V]'] / Battery_Dataframe['R1 [Ohm]'].values)

#Schritt 7 - Simulation for U_R1 [V] and I_R1 [A]
# Initialize an array for storing U_R1 values with the initial condition
U_R2_out = np.zeros_like(Battery_Dataframe["Zeit [s]"].values)

# Time steps (assuming uniform time step from the dataframe's index)
t = Battery_Dataframe["Zeit [s]"].values

for i in range(1, len(t)):
    tspan = [t[i-1], t[i]]
    R2, Current, C2 = Battery_Dataframe['R2 [Ohm]'].values[i], Battery_Dataframe['Current [A]'].values[i], Battery_Dataframe['C2 [Ohm]'].values[i]
    U_R2 = odeint(lambda U_R2, t: (Current - U_R2 / R2) / C2, U_R2_out[i-1], tspan)[-1]
    U_R2_out[i] = U_R2[0]

Battery_Dataframe['U_R2 [V]'] = U_R2_out
Battery_Dataframe['I_2 [A]'] = (Battery_Dataframe['U_R2 [V]'] / Battery_Dataframe['R2 [Ohm]'].values)

# Schritt 9 - Addieren aller Spannungen und multiplizieren
#Battery_Dataframe["U_ges [V]"] = Battery_Dataframe['OCV [V]'] + Battery_Dataframe['U_R1 [V]'] + Battery_Dataframe['U_R2 [V]']
#U_ges_current = Battery_Dataframe["U_ges [V]"]

plot(Battery_Dataframe, "Zeit [s]", 'Leistung [W]')
plot(Battery_Dataframe, "Zeit [s]", 'Current [A]')
plot(Battery_Dataframe, "Zeit [s]", 'Charge [C]')
plot(Battery_Dataframe, "Zeit [s]", 'SOC [%]')
plot(Battery_Dataframe, "Zeit [s]", 'OCV [V]')
plot(Battery_Dataframe, "Zeit [s]", 'R [Ohm]')
plot(Battery_Dataframe, "Zeit [s]", 'R1 [Ohm]')
plot(Battery_Dataframe, "Zeit [s]", 'R2 [Ohm]')
plot(Battery_Dataframe, "Zeit [s]", 'C1 [Ohm]')
plot(Battery_Dataframe, "Zeit [s]", 'C2 [Ohm]')
plot(Battery_Dataframe, "Zeit [s]", "U_R [V]")
plot(Battery_Dataframe, "Zeit [s]", "U_R1 [V]")
plot(Battery_Dataframe, "Zeit [s]", "I_1 [A]")
plot(Battery_Dataframe, "Zeit [s]", "U_R2 [V]")
plot(Battery_Dataframe, "Zeit [s]", "I_2 [A]")