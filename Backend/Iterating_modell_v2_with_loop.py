
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


def lookup_1d(SOC, SOC_breakpoints, delta_OCV_data):
    # Perform interpolation for the given SOC
    interpolated_value = np.interp(SOC, SOC_breakpoints, delta_OCV_data)

    # If the result is NaN (although unlikely with 1D interpolation), find the nearest value
    if np.isnan(interpolated_value):
        nearest_SOC_index = np.argmin(np.abs(np.array(SOC_breakpoints) - SOC))
        interpolated_value = delta_OCV_data[nearest_SOC_index]

    return interpolated_value


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




# 1. Pre-allocate columns with default values
Battery_Dataframe['Leistung [W]'] = 0
Battery_Dataframe['Current [A]'] = 0
Battery_Dataframe['Charge [C]'] = 0
Battery_Dataframe['SOC [%]'] = soc_init  # Initialize with `soc_init`

# Assuming t is a column in Battery_Dataframe
t = Battery_Dataframe['Zeit [s]']
U_R1_out = np.zeros_like(Battery_Dataframe["Zeit [s]"].values)
Battery_Dataframe['U_R1 [V]'] = 0.0
Battery_Dataframe['I_R1 [A]'] = 0.0

Battery_Dataframe['U_R2 [V]'] = 0.0
Battery_Dataframe['I_R2 [A]'] = 0.0
Battery_Dataframe['Q_Irrev [W]'] = 0

Battery_Dataframe['U_ges [V]'] = 0.0
init_volt = 3.6 * 13
Battery_Dataframe.at[0, 'U_ges [V]'] = init_volt

for i in range(1, len(t)):

    # Current time step value extraction
    Leistung_kW = Battery_Dataframe.at[i, 'Leistung [kW]']

    # Step 1: Convert Kilowatt to Watt in thermodynamically correct direction
    Leistung_W = Leistung_kW * -1000
    Battery_Dataframe.at[i, 'Leistung [W]'] = Leistung_W

    # Step 2: Convert Watt to Ampere by dividing by voltage
    Current_A = Leistung_W / init_volt
    Battery_Dataframe.at[i, 'Current [A]'] = Current_A

    # Step 3: Calculate Charge from Current
    delta_t = t[i] - t[i - 1]
    Battery_Dataframe.at[i, 'Charge [C]'] = Battery_Dataframe.at[i - 1, 'Charge [C]'] + Current_A * delta_t

    # Step 4: Convert Charge to SOC
    denumerator_qzelle = 1 / q_zelle
    stunden_zu_sekunde = 1 / 3600
    prozent = 100
    soc = Battery_Dataframe.at[i, 'Charge [C]'] * denumerator_qzelle * stunden_zu_sekunde * prozent
    soc += soc_init
    Battery_Dataframe.at[i, 'SOC [%]'] = max(0, min(100, soc))  # Clipping values between 0 and 100

    # Step 5: Calculate Ohmic Quantities

    # Set the current temperature
    Battery_Dataframe.at[i, 'Temperatur [K]'] = Temperature

    # 5.1: Calculate OCV

    subset_df = Battery_Dataframe.iloc[[i]].reset_index(drop=True)
    subset_df = fast_lookup_2d(subset_df, soc_steps_ocv, temp_steps, ocv)
    Battery_Dataframe.at[i, 'OCV [V]'] = subset_df.at[0, 'Interpolated Value']


    # 5.2: Calculate R
    subset_df = Battery_Dataframe.iloc[[i]].reset_index(drop=True)
    subset_df = fast_lookup_2d(subset_df, SOCsteps, temp_steps, R)
    Battery_Dataframe.at[i, 'R [Ohm]'] = subset_df.at[0, 'Interpolated Value']

    # 5.3: Calculate R1
    subset_df = Battery_Dataframe.iloc[[i]].reset_index(drop=True)
    subset_df = fast_lookup_2d(subset_df, SOCsteps, temp_steps, R1)
    Battery_Dataframe.at[i, 'R1 [Ohm]'] = subset_df.at[0, 'Interpolated Value']

    # 5.4: Calculate R2
    subset_df = Battery_Dataframe.iloc[[i]].reset_index(drop=True)
    subset_df = fast_lookup_2d(subset_df, SOCsteps, temp_steps, R2)
    Battery_Dataframe.at[i, 'R2 [Ohm]'] = subset_df.at[0, 'Interpolated Value']

    # 5.5: Calculate C1
    subset_df = Battery_Dataframe.iloc[[i]].reset_index(drop=True)
    subset_df = fast_lookup_2d(subset_df, SOCsteps, temp_steps, C1)
    Battery_Dataframe.at[i, 'C1 [Ohm]'] = subset_df.at[0, 'Interpolated Value']

    # 5.6: Calculate C2
    subset_df = Battery_Dataframe.iloc[[i]].reset_index(drop=True)
    subset_df = fast_lookup_2d(subset_df, SOCsteps, temp_steps, C2)
    Battery_Dataframe.at[i, 'C2 [Ohm]'] = subset_df.at[0, 'Interpolated Value']


    Battery_Dataframe.at[i, 'U_R [V]'] = Battery_Dataframe.at[i, 'R [Ohm]'] * Battery_Dataframe.at[i, 'Current [A]']

    # 5.7: Calculate I_ri
    R1_current = Battery_Dataframe.at[i, 'R1 [Ohm]']
    U_R1_prev = Battery_Dataframe.at[i - 1, 'U_R1 [V]']
    I_R1 = U_R1_prev / R1_current
    Battery_Dataframe.at[i, 'I_R1 [A]'] = I_R1

    # 5.8: Calculate b
    b = Current_A - I_R1

    # 5.9: Calculate c
    C1_current = Battery_Dataframe.at[i, 'C1 [Ohm]']  # Assuming C1 is in Ohm and not in F (farads).
    c = b / C1_current

    # 5.10: Integrate c using the trapezoidal rule
    dt = t[i] - t[i - 1]
    U_R1_current, _, _ = simulate_UR_n_and_IR_n_trapezoidal(R1_current, Current_A, C1_current, U_R1_prev, c, dt)
    Battery_Dataframe.at[i, 'U_R1 [V]'] = U_R1_current

    # 5.7: Calculate I_ri
    R1_current = Battery_Dataframe.at[i, 'R1 [Ohm]']
    U_R1_prev = Battery_Dataframe.at[i - 1, 'U_R1 [V]']
    I_R1 = U_R1_prev / R1_current
    Battery_Dataframe.at[i, 'I_R1 [A]'] = I_R1

    # 5.8: Calculate b
    b = Current_A - I_R1

    # 5.9: Calculate c
    C1_current = Battery_Dataframe.at[i, 'C1 [Ohm]']  # Assuming C1 is in Ohm and not in F (farads).
    c = b / C1_current

    # 5.10: Integrate c using the trapezoidal rule
    dt = t[i] - t[i - 1]
    U_R1_current, _, _ = simulate_UR_n_and_IR_n_trapezoidal(R1_current, Current_A, C1_current, U_R1_prev, c, dt)
    Battery_Dataframe.at[i, 'U_R1 [V]'] = U_R1_current


    # 5.7: Calculate I_R2
    R2_current = Battery_Dataframe.at[i, 'R2 [Ohm]']
    U_R2_prev = Battery_Dataframe.at[i - 1, 'U_R2 [V]']
    I_R2 = U_R2_prev / R2_current
    Battery_Dataframe.at[i, 'I_R2 [A]'] = I_R2

    # 5.8: Calculate b
    b = Current_A - I_R2

    # 5.9: Calculate c
    C2_current = Battery_Dataframe.at[i, 'C2 [Ohm]']  # Assuming C1 is in Ohm and not in F (farads).
    c = b / C2_current

    # 5.10: Integrate c using the trapezoidal rule
    dt = t[i] - t[i - 1]
    U_R2_current, _, _ = simulate_UR_n_and_IR_n_trapezoidal(R2_current, Current_A, C2_current, U_R2_prev, c, dt)
    Battery_Dataframe.at[i, 'U_R2 [V]'] = U_R2_current

    U_ges_current = (
            Battery_Dataframe.at[i, 'U_R1 [V]'] +
            Battery_Dataframe.at[i, 'U_R2 [V]'] +
            Battery_Dataframe.at[i, 'U_R [V]'] +
            Battery_Dataframe.at[i, 'OCV [V]']
    ) * 13

    # Store the computed value in the dataframe
    Battery_Dataframe.at[i, 'U_ges [V]'] = U_ges_current

    # Use the current value as the init_volt for the next cycle
    init_volt = U_ges_current


    # Calculate Q_Irrev components based on the provided formulas
    Q_R = Battery_Dataframe.at[i, 'R [Ohm]'] * (Battery_Dataframe.at[i, 'Current [A]']**2)
    Q_R1 = Battery_Dataframe.at[i, 'R1 [Ohm]'] * (Battery_Dataframe.at[i, 'I_R1 [A]']**2)
    Q_R2 = Battery_Dataframe.at[i, 'R2 [Ohm]'] * (Battery_Dataframe.at[i, 'I_R2 [A]']**2)

    # Sum the components to compute Q_Irrev
    Q_Irrev = Q_R + Q_R1 + Q_R2

    # Store the computed value in the dataframe
    Battery_Dataframe.at[i, 'Q_Irrev [W]'] = Q_Irrev

    SOC_current = Battery_Dataframe.at[i, 'SOC [%]']
    Battery_Dataframe.at[i, "Delta OCV [V]"] = lookup_1d(SOC_current, SOCsteps_Takano, DeltaOCVdT)


    ### Here debugging
    Battery_Dataframe.at[i, "Q_Rev [W]"] = (Battery_Dataframe.at[i, 'Temperatur [K]'] *
                                            Battery_Dataframe.at[i, 'Current [A]'] *
                                            SOC_current)

    Battery_Dataframe.at[i, "Q_Cell [W]"] = (Battery_Dataframe.at[i, "Q_Rev [W]"] +
                                             Battery_Dataframe.at[i, 'Q_Irrev [W]']) * 13


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
plot(Battery_Dataframe, "Zeit [s]", 'U_R [V]')
plot(Battery_Dataframe, "Zeit [s]", 'U_R1 [V]')
plot(Battery_Dataframe, "Zeit [s]", 'I_R1 [A]')
plot(Battery_Dataframe, "Zeit [s]", 'U_R2 [V]')
plot(Battery_Dataframe, "Zeit [s]", 'I_R2 [A]')
plot(Battery_Dataframe, "Zeit [s]", 'U_ges [V]')
plot(Battery_Dataframe, "Zeit [s]", 'Q_Irrev [W]')
plot(Battery_Dataframe, "Zeit [s]", "Delta OCV [V]")
plot(Battery_Dataframe, "Zeit [s]", 'Temperatur [K]')
plot(Battery_Dataframe, "Zeit [s]", "Q_Rev [W]")
plot(Battery_Dataframe, "Zeit [s]", "Q_Cell [W]")
