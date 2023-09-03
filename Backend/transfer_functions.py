from scipy.integrate import cumtrapz

def perform_integration(dataframe, column_to_manipulate, new_columnname, dt=0.5):
    integrated_dataframe = dataframe.copy()
    input_signal = integrated_dataframe[column_to_manipulate].values

    # Use the trapezoidal rule for integration from scipy
    output_signal = cumtrapz(input_signal, dx=dt, initial=0)

    integrated_dataframe[new_columnname] = output_signal
    return integrated_dataframe
