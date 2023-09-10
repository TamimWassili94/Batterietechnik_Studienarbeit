import pandas as pd
import matplotlib.pyplot as plt
from transfer_functions import RK4

Battery_Dataframe = pd.read_csv('BatteryData_2.csv')

def U_R1(dataframe):
    integrated_value = 0  # Initialize the integrated value
    dt = 0.5  # Time step for integration

    # Define the function to be integrated with RK4
    f = lambda y, u: u

    # Initialize arrays for holding input and output values
    input_signal = dataframe['irgendwas2'].values  # Assuming 'irgendwas2' is what we want to integrate
    output_signal = perform_integration_rk4(dataframe, 'irgendwas2', 'integrated_irgendwas2', dt)

    # Loop through the DataFrame rows
    for index, row in dataframe.iterrows():
        # Update 'irgendwas' and 'irgendwas2'
        dataframe.at[index, 'I_R1'] = dataframe.at[index, 'U_R1'] / row['R1']
        dataframe.at[index, 'irgendwas'] = row['Strom [A]'] - dataframe.at[index, 'I_R1']
        dataframe.at[index, 'irgendwas2'] = dataframe.at[index, 'irgendwas'] / row['C1']

        # Integrate 'irgendwas2' using RK4
        integrated_value = output_signal[index]  # Retrieve the integrated value for the current index

        # Update U_R1, I_R1, and integrated_value ('dU_R1/dt')
        dataframe.at[index, 'U_R1'] = row['R1'] * integrated_value
        dataframe.at[index, 'I_R1'] = dataframe.at[index, 'U_R1'] / row['R1']
        dataframe.at[index, 'dU_R1/dt'] = integrated_value

    print(dataframe)  # Print the DataFrame for debugging
    return dataframe  # Return the modified DataFrame

def perform_integration_rk4(dataframe, column_to_manipulate, new_columnname, dt=0.5):
    integrated_dataframe = dataframe.copy()
    input_signal = integrated_dataframe[column_to_manipulate].values

    f = lambda y, u: u  # Here, 'u' is the input from 'input_signal'

    output_signal = RK4(f, 0, dt, len(input_signal), input_signal)  # Start from 0

    integrated_dataframe[new_columnname] = output_signal
    return integrated_dataframe[new_columnname]



batterydata = U_R1(Battery_Dataframe)

plt.plot(batterydata.index, batterydata["U_R1"])

# Add labels and title
plt.xlabel("Index")
plt.ylabel("U_R1")
plt.title("Plot of U_R1")

# Show the plot
plt.show()


