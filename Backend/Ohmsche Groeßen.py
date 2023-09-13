import pandas as pd
import matplotlib.pyplot as plt
from transfer_functions import perform_integration_rk4

Battery_Dataframe = pd.read_csv('BatteryData_2.csv')

def simulate_UR1_euler(Battery_Dataframe, Resistor_Row, Current_Row, Condensator_Row):
    initial_output = 0  # initial value for output
    dt = 0.5  # time step
    output_voltage_list = []
    output_current_list = []

    for index, row in Battery_Dataframe.iterrows():
        R1 = row[Resistor_Row]
        I_Zelle = row[Current_Row]
        C1 = row[Condensator_Row]

        # Step 1: Divide output by R1
        Current = initial_output / R1 if R1 != 0 else 0

        # Step 2: Subtract Current from I_Zelle
        Delta_Current = I_Zelle - Current

        # Step 3: Divide Value2 by C1
        Gradient_of_Voltage = Delta_Current / C1 if C1 != 0 else 0

        # Step 4: Euler integration to produce new output
        new_output = initial_output + Gradient_of_Voltage * dt

        # Save new output for the next iteration
        initial_output = new_output
        output_voltage_list.append(initial_output)
        output_current_list.append(Current)

    # Add the output signal to the original dataframe
    Battery_Dataframe['U_R1 [V]'] = output_voltage_list
    Battery_Dataframe['I_R1 [A]'] = output_current_list

    return Battery_Dataframe

#Battery_Dataframe = simulate_UR1_euler(Battery_Dataframe, "R1", "Strom [A]", "C1")

# Assuming your DataFrame is called Battery_Dataframe
#ax = Battery_Dataframe.plot(x='Zeit [s]', y='U_R1 [V]')
#plt.xlabel('Zeit [S]')
#plt.ylabel('U_R1 [V]')
#plt.title('Voltage over Time - Euler')
#ax.grid(True)  # This line adds grid lines
#plt.show()

def simulate_UR(Battery_Dataframe, Resistor_Row, Current_Row):
    output_list_voltage = []

    for index, row in Battery_Dataframe.iterrows():
        R = row[Resistor_Row]
        I_Zelle = row[Current_Row]

        #Step1: Multiply R with I
        U_R = R * I_Zelle

        #Step2: Append into list
        output_list_voltage.append(U_R)

    Battery_Dataframe['U_R [V]'] = output_list_voltage
    return Battery_Dataframe

Battery_Dataframe = simulate_UR(Battery_Dataframe, "R1", "Strom [A]")

def plot_single_element(x_axis, y_axis, title, unit):
    # Create the plot and store the axis object
    ax = Battery_Dataframe.plot(x=x_axis, y=y_axis, label=y_axis)

    # Customize the plot
    plt.xlabel(x_axis)
    plt.ylabel(f'{title} {unit}')
    plt.title(f'{title} over Time - Trapezoid')
    ax.grid(True)  # This line adds grid lines

    ax.legend()
    plt.show()

plot_single_element('Zeit [s]', 'U_R [V]', 'Voltage', '[V]')


def simulate_UR_n_and_IR_n_trapezoidal(Battery_Dataframe, Resistor_Row, Current_Row, Condensator_Row, Voltage_Str, Current_Str):

    initial_output = 0  # initial value for output
    dt = 0.5  # time step
    prev_value3 = 0  # store the previous value for the Trapezoidal rule
    output_list_voltage = []
    output_list_current = []

    for index, row in Battery_Dataframe.iterrows():
        R1 = row[Resistor_Row]
        I_Zelle = row[Current_Row]
        C1 = row[Condensator_Row]

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
        output_list_voltage.append(initial_output)
        output_list_current.append(Current)

    # Add the output signal to the original dataframe
    Battery_Dataframe[Voltage_Str] = output_list_voltage
    Battery_Dataframe[Current_Str] = output_list_current

    return Battery_Dataframe

Battery_Dataframe = simulate_UR_n_and_IR_n_trapezoidal(Battery_Dataframe, "R1", "Strom [A]", "C1", 'U_R1 [V]', 'I_R1 [A]')
Battery_Dataframe = simulate_UR_n_and_IR_n_trapezoidal(Battery_Dataframe, "R2", "Strom [A]", "C2", 'U_R2 [V]', 'I_R2 [A]')

def plot_2_elements(x_axis, y_axis1, y_axis2, title, unit):
    # Create the first plot and store the axis object
    ax = Battery_Dataframe.plot(x=x_axis, y=y_axis1, label=y_axis1)

    # Use the same axis object for the second plot
    Battery_Dataframe.plot(x=x_axis, y=y_axis2, ax=ax, label=y_axis2)

    # Customize the plot
    plt.xlabel(x_axis)
    plt.ylabel(f'{title} {unit}')
    plt.title(f'{title} over Time - Trapezoid')
    ax.grid(True)  # This line adds grid lines

    ax.legend()
    plt.show()


plot_2_elements('Zeit [s]', 'U_R1 [V]', 'U_R2 [V]', 'Voltage', '[V]')
plot_2_elements('Zeit [s]', 'I_R1 [A]', 'I_R2 [A]', 'Ampere', '[A]')
