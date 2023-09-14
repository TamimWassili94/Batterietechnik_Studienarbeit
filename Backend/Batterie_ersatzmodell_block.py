import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, interp1d

# importieren von parametern aus anderer .py
from Initial_Parameters import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2)


Battery_Dataframe = pd.read_csv('BatteryData_1.csv')

# Hinweis: Die hier erhaltenen extrapolierten Werte können von denen in Simulink abweichen.
# Diese Abweichung ist auf die inhärenten Unterschiede in den mathematischen
# Ansätzen zurückzuführen, die von der scipy-Bibliothek in Python und MATLAB/Simulink
# für die Interpolation und Extrapolation verwendet werden.
# Insbesondere ist die hier verwendete 1D-Extrapolationsstrategie ein naiver Ansatz, der die
# extrapolierten Werte entlang der SOC- und Temperaturachsen mittelt. Dies entspricht möglicherweise
# nicht den komplexeren, integrierten Algorithmen von Simulink für n-D-Lookup-Tabellen-Extrapolation.
def lookup_2d(row, SOC_breakpoints, Temp_breakpoints, table_data):
    SOC = row['SOC']
    Temp = row['Temp']
    i = 0
    print(i, SOC)
    i += 1
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

# Für Temp werden gerade konstante Werte angenommen da es noch keine temperatursimulation gibt.
SOC_DATAFRAME = pd.DataFrame({
    'SOC': Battery_Dataframe["SOC [%]"],
    'Temp': np.full(2361, 298.15),
    'Zeit [s]': Battery_Dataframe['Zeit [s]']
})

Battery_Dataframe['OCV'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(soc_steps_ocv, temp_steps, ocv))

#R ist bei konstanter Temperatur auch konstant
Battery_Dataframe['R'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, R))

#R ist bei konstanter Temperatur auch konstant
Battery_Dataframe['R1'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, R1))

Battery_Dataframe['C1'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, C1))

Battery_Dataframe['R2'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, R2))

Battery_Dataframe['C2'] = SOC_DATAFRAME.apply(lookup_2d, axis=1, args=(SOCsteps, temp_steps, C2))

def plot_OCV_values(df, column_name, unit, x_axis_column="Zeit [s]"):
    """
    Plot the OCV values from the given dataframe.

    Parameters:
    - df: DataFrame containing the OCV column.
    - column_name: string representing the column name for y-axis
    - unit: string representing the unit for y-axis
    - x_axis_column: string representing the column name for x-axis (default is None, which uses the DataFrame index)
    """

    plt.figure(figsize=(10, 6))

    if x_axis_column is None:
        x_data = df.index
    else:
        x_data = df[x_axis_column]

    plt.plot(x_data, df[column_name], label=column_name)
    plt.title(column_name)
    plt.xlabel('timestamps' if x_axis_column is None else x_axis_column)
    plt.ylabel(f"{column_name}  {unit}")
    plt.grid(True)
    plt.legend()
    plt.show()


plot_OCV_values(Battery_Dataframe, "OCV", "-")
plot_OCV_values(Battery_Dataframe, "R", "(V)")
plot_OCV_values(Battery_Dataframe, "R1", "(V)")
plot_OCV_values(Battery_Dataframe, "C1", "(Coloumbina)")
plot_OCV_values(Battery_Dataframe, "R2", "(V)")
plot_OCV_values(Battery_Dataframe, "C2", "(Coloumbina)")


Battery_Dataframe.to_csv('BatteryData_2.csv', index=False)