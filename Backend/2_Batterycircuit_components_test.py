from scipy.interpolate import griddata
import numpy as np
import pandas as pd
from SOC_Block_in_Python import soc
import matplotlib.pyplot as plt


from Initial_Parameters import soc_steps_ocv, ocv, temp_steps, R, SOCsteps


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

# Define your data here
SOCsteps = np.array([30, 40, 50, 60, 70])  # Example SOC breakpoints
Tsteps = np.array([253.15, 263.15, 283.15, 298.15, 313.15, 323.15])  # Example Temp breakpoints
R_values = np.array([0.015456, 0.008921403, 0.003025827, 0.00178, 0.0013081, 0.0011997])
R = np.outer(R_values, np.ones(len(SOCsteps)))  # Create the table data

# Test the function
df = pd.DataFrame({
    'SOC': soc["SOC [%]"],
    'Temp': np.full(2361, 298.15)
})

df['R'] = df.apply(lookup_2d, axis=1, args=(SOCsteps, Tsteps, R))
print(df)

df['OCV'] = df.apply(lookup_2d, axis=1, args=(soc_steps_ocv, temp_steps, ocv))
print(df)

def plot_OCV_values(df):
    """
    Plot the OCV values from the given dataframe.

    Parameters:
    - df: DataFrame containing the OCV column.
    """

    plt.figure(figsize=(10, 6))
    plt.plot(df['OCV'], '-o', label='R')
    plt.title('Open Circuit Voltage (R) Values')
    plt.xlabel('Index')
    plt.ylabel('R (R)')
    plt.grid(True)
    plt.legend()
    plt.show()


plot_OCV_values(df)