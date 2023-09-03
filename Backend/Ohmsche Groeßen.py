import pandas as pd
import matplotlib.pyplot as plt


batterydata = pd.read_csv('BatteryData_2.csv')

def U_R1(dataframe):
    integrated_value = 0  # Initialize the integrated value
    dt = 2  # Time step for integration

    # Loop through the DataFrame rows
    for index, row in dataframe.iterrows():
        # Calculate U_R1, I_R1, and 'irgendwas'
        dataframe.at[index, "U_R1"] = row["R1"] * integrated_value
        dataframe.at[index, 'I_R1'] = dataframe.at[index, 'U_R1'] / row['R1']
        dataframe.at[index, 'irgendwas'] = row['Strom [A]'] -dataframe.at[index, 'I_R1']
        dataframe.at[index, 'irgendwas2'] = dataframe.at[index, 'irgendwas'] / row['C1']

        # Add integration calculation for 'irgendwas' using simple rectangular integration
        integrated_value += dataframe.at[index, "irgendwas2"] * dt
        dataframe.at[index, 'dU_R1/dt'] = integrated_value  # Store the integrated value in a new column


    print(dataframe)  # Print the DataFrame for debugging
    return dataframe  # Return the modified DataFrame


batterydata = U_R1(batterydata)

plt.plot(batterydata.index, batterydata["U_R1"])

# Add labels and title
plt.xlabel("Index")
plt.ylabel("U_R1")
plt.title("Plot of U_R1")

# Show the plot
plt.show()


