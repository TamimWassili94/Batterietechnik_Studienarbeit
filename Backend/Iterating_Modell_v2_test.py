import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import control as ctrl
from scipy.interpolate import griddata, interp1d

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

def lookup_2d_wrapper(dataframe, SOC_breakpoints, Temp_breakpoints, table_data):
    result_df = fast_lookup_2d(dataframe, SOC_breakpoints, Temp_breakpoints, table_data)
    return result_df['Interpolated Value']



#Schritt 1 - Kilowatt zu Watt in thermodynamisch richtiger Richtung
Battery_Dataframe['Leistung [W]'] = Battery_Dataframe['Leistung [kW]'] * -1000
plot(Battery_Dataframe, "Zeit [s]", 'Leistung [W]')

#Schritt 2 - Watt zu Ampere durch Division mit der Spannung
init_volt = 3.6*13
Battery_Dataframe['Current [A]'] = Battery_Dataframe['Leistung [W]'] / init_volt
plot(Battery_Dataframe, "Zeit [s]", 'Current [A]')

#Schritt 3 - Berechnung von Ampere zu Ladung
integrate_dataframe(Battery_Dataframe, 'Current [A]', 'Zeit [s]', 'Charge [C]')
plot(Battery_Dataframe, "Zeit [s]", 'Charge [C]')

#Schritt 4 - Berechnung von Ladung zu SOC
denumerator_qzelle = 1/q_zelle
stunden_zu_sekunde = 1/3600
prozent = 100
Battery_Dataframe['SOC [%]'] = Battery_Dataframe['Charge [C]'] * denumerator_qzelle * stunden_zu_sekunde * prozent
Battery_Dataframe['SOC [%]'] = Battery_Dataframe['SOC [%]'] + soc_init
plot(Battery_Dataframe, "Zeit [s]", 'SOC [%]')
Battery_Dataframe['SOC [%]'] = Battery_Dataframe['SOC [%]'].clip(0, 100)  # Beschränkt die Werte auf den Bereich [0, 100]
plot(Battery_Dataframe, "Zeit [s]", 'SOC [%]')

#Schritt 5 - Berechnung von Ohmschen Größen
Battery_Dataframe['Temperatur [K]'] = Temperature
##Schritt 5.1 - Berechnung vom OCV
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, soc_steps_ocv, temp_steps, ocv)
Battery_Dataframe.rename(columns={'Interpolated Value': 'OCV [V]'}, inplace=True)
plot(Battery_Dataframe, "Zeit [s]", 'OCV [V]')
##Schritt 5.2 - Berechnung von R
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, R)
Battery_Dataframe.rename(columns={'Interpolated Value': 'R [Ohm]'}, inplace=True)
plot(Battery_Dataframe, "Zeit [s]", 'R [Ohm]')
##Schritt 5.3 - Berechnung von R1
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, R1)
Battery_Dataframe.rename(columns={'Interpolated Value': 'R1 [Ohm]'}, inplace=True)
plot(Battery_Dataframe, "Zeit [s]", 'R1 [Ohm]')
##Schritt 5.4 - Berechnung von R2
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, R2)
Battery_Dataframe.rename(columns={'Interpolated Value': 'R2 [Ohm]'}, inplace=True)
plot(Battery_Dataframe, "Zeit [s]", 'R2 [Ohm]')
##Schritt 5.5 - Berechnung von C1
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, C1)
Battery_Dataframe.rename(columns={'Interpolated Value': 'C1 [Ohm]'}, inplace=True)
plot(Battery_Dataframe, "Zeit [s]", 'C1 [Ohm]')
##Schritt 5.6 - Berechnung von C2
Battery_Dataframe = fast_lookup_2d(Battery_Dataframe, SOCsteps, temp_steps, C2)
Battery_Dataframe.rename(columns={'Interpolated Value': 'C2 [Ohm]'}, inplace=True)
plot(Battery_Dataframe, "Zeit [s]", 'C2 [Ohm]')