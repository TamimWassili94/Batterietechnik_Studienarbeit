import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from SOC_Block_in_Python import soc
import matplotlib.pyplot as plt

def lookup_2d(row, SOC_breakpoints, Temp_breakpoints, OCV_data):
    """
    Create a 2D lookup table using the given data and interpolate to find OCV.

    Parameters:
    - row: A row from a dataframe containing SOC and Temp columns
    - SOC_breakpoints: SOC values from your data
    - Temp_breakpoints: Temperature values from your data
    - OCV_data: OCV values corresponding to the SOC and Temp breakpoints

    Returns:
    Interpolated OCV value for the SOC and Temp in the row.
    """

    SOC = row['SOC']
    Temp = row['Temp']

    # Create the interpolating function based on the given data
    interp_func = RegularGridInterpolator((Temp_breakpoints, SOC_breakpoints), OCV_data)

    # Use the function to interpolate OCV for the given SOC and Temp
    return interp_func(np.array([[Temp, SOC]]))[0]


# Your data
SOCsteps_OCV = np.arange(0, 101, 10)
Tsteps = np.array([253.15, 263.15, 283.15, 298.15, 313.15, 323.15])
OCV_single_row = np.array([3.3383, 3.4305, 3.5207, 3.5875, 3.6381, 3.7006, 3.7786, 3.8741, 3.9564, 4.0601, 4.1651])
OCV = np.tile(OCV_single_row, (len(Tsteps), 1))

# Sample dataframe with your input data
df = pd.DataFrame({
    'SOC': soc["SOC [%]"],
    'Temp': np.full(2361, 255)
})

df['OCV'] = df.apply(lookup_2d, axis=1, args=(SOCsteps_OCV, Tsteps, OCV))
print(df)


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


plot_OCV(df)


def plot_OCV_values(df):
    """
    Plot the OCV values from the given dataframe.

    Parameters:
    - df: DataFrame containing the OCV column.
    """

    plt.figure(figsize=(10, 6))
    plt.plot(df['OCV'], '-o', label='OCV')
    plt.title('Open Circuit Voltage (OCV) Values')
    plt.xlabel('Index')
    plt.ylabel('OCV (V)')
    plt.grid(True)
    plt.legend()
    plt.show()


plot_OCV_values(df)