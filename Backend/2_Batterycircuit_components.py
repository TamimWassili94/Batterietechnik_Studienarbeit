import numpy as np
import pandas as pd
from SOC_Block_in_Python import soc
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# importieren von parametern aus anderer .py
from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2)



def lookup_2d(row, SOC_breakpoints, Temp_breakpoints, table_data):
    SOC = row['SOC']
    Temp = row['Temp']

    # If SOC or Temp is out of range, manually set to the closest value within range
    if SOC < min(SOC_breakpoints):
        SOC = min(SOC_breakpoints)
    if SOC > max(SOC_breakpoints):
        SOC = max(SOC_breakpoints)

    if Temp < min(Temp_breakpoints):
        Temp = min(Temp_breakpoints)
    if Temp > max(Temp_breakpoints):
        Temp = max(Temp_breakpoints)

    # Create grid and multivariate data points
    points = np.array([[t, s] for t in Temp_breakpoints for s in SOC_breakpoints])
    values = table_data.flatten()

    # Perform the interpolation
    interp_val = griddata(points, values, (Temp, SOC), method='linear')
    return interp_val


# Für Temp werden gerade konstante Werte angenommen da es noch keine temperatursimulation gibt.
SOC_DATAFRAME = pd.DataFrame({
    'SOC': soc["SOC [%]"],
    'Temp': np.full(2361, 298.15)
})

SOC_DATAFRAME['OCV'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(soc_steps_ocv, temp_steps, ocv))

#R ist bei konstanter Temperatur auch konstant
SOC_DATAFRAME['R'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, R))

#R ist bei konstanter Temperatur auch konstant
SOC_DATAFRAME['R1'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, R1))

SOC_DATAFRAME['C1'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, C1))

SOC_DATAFRAME['R2'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, R2))

SOC_DATAFRAME['C2'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, C2))
def plot_OCV(df):
    """
    Plot the OCV against SOC from the given dataframe.

    Parameters:
    - df: DataFrame containing SOC and OCV columns.
    """

    plt.figure(figsize=(10, 6))
    plt.plot(df['SOC'], df['OCV'], '-o', label='OCV')
    plt.title('Open Circuit Voltage (OCV) vs. State of Charge (SOC)')
    plt.xlabel('SOC (%)')
    plt.ylabel('OCV (V)')
    plt.grid(True)
    plt.legend()
    plt.show()


plot_OCV(SOC_DATAFRAME)


def plot_OCV_values(df, column_name, unit):
    """
    Plot the OCV values from the given dataframe.

    Parameters:
    - df: DataFrame containing the OCV column.
    - column_name = string of SOC
    """

    plt.figure(figsize=(10, 6))
    plt.plot(df[column_name], '-o', label=column_name)
    plt.title(column_name)
    plt.xlabel('timestamps')
    plt.ylabel(f"{column_name}  {unit}")
    plt.grid(True)
    plt.legend()
    plt.show()


plot_OCV_values(SOC_DATAFRAME, "OCV", "-")
plot_OCV_values(SOC_DATAFRAME, "R", "(V)")
plot_OCV_values(SOC_DATAFRAME, "R1", "(V)")
plot_OCV_values(SOC_DATAFRAME, "C1", "(Coloumbina)")
plot_OCV_values(SOC_DATAFRAME, "R2", "(V)")
plot_OCV_values(SOC_DATAFRAME, "C2", "(Coloumbina)")