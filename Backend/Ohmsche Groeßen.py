import pandas as pd
import matplotlib.pyplot as plt
from transfer_functions import perform_integration_rk4

Battery_Dataframe = pd.read_csv('BatteryData_2.csv')

def simulate_system_with_euler(Battery_Dataframe):
    initial_output = 0  # initial value for output
    dt = 0.5  # time step
    output_list = []

    for index, row in Battery_Dataframe.iterrows():
        R1 = row['R1']
        I_Zelle = row['Strom [A]']
        C1 = row['C1']

        # Step 1: Divide output by R1
        Value1 = initial_output / R1 if R1 != 0 else 0

        # Step 2: Subtract Value1 from I_Zelle
        Value2 = I_Zelle - Value1

        # Step 3: Divide Value2 by C1
        Value3 = Value2 / C1 if C1 != 0 else 0

        # Step 4: Euler integration to produce new output
        new_output = initial_output + Value3 * dt

        # Save new output for the next iteration
        initial_output = new_output
        output_list.append(initial_output)

    # Add the output signal to the original dataframe
    Battery_Dataframe['output'] = output_list

    return Battery_Dataframe



Battery_Dataframe = simulate_system_with_euler(Battery_Dataframe)

# Assuming your DataFrame is called Battery_Dataframe
ax = Battery_Dataframe.plot(x='Zeit [s]', y='output')
plt.xlabel('Zeit [S]')
plt.ylabel('Output')
plt.title('Output over Time')
ax.grid(True)  # This line adds grid lines
plt.show()


def simulate_system_with_trapezoidal(Battery_Dataframe):
    initial_output = 0  # initial value for output
    dt = 0.5  # time step
    prev_value3 = 0  # store the previous value for the Trapezoidal rule
    output_list = []

    for index, row in Battery_Dataframe.iterrows():
        R1 = row['R1']
        I_Zelle = row['Strom [A]']
        C1 = row['C1']

        # Step 1: Divide output by R1
        Value1 = initial_output / R1 if R1 != 0 else 0

        # Step 2: Subtract Value1 from I_Zelle
        Value2 = I_Zelle - Value1

        # Step 3: Divide Value2 by C1
        Value3 = Value2 / C1 if C1 != 0 else 0

        # Step 4: Trapezoidal Rule integration to produce new output
        new_output = initial_output + (Value3 + prev_value3) * dt / 2

        # Save new output for the next iteration
        initial_output = new_output
        prev_value3 = Value3
        output_list.append(initial_output)

    # Add the output signal to the original dataframe
    Battery_Dataframe['output'] = output_list

    return Battery_Dataframe

Battery_Dataframe = simulate_system_with_trapezoidal(Battery_Dataframe)

# Assuming your DataFrame is called Battery_Dataframe
ax = Battery_Dataframe.plot(x='Zeit [s]', y='output')
plt.xlabel('Zeit [S]')
plt.ylabel('Output')
plt.title('Output over Time')
ax.grid(True)  # This line adds grid lines
plt.show()