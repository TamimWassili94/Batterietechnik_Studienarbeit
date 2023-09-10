from scipy.integrate import cumtrapz
import numpy as np

def RK4(f, y0, dt, n, input_signal):
    y = np.zeros(n)
    y[0] = y0

    for i in range(1, n):
        k1 = f(y[i - 1], input_signal[i])
        k2 = f(y[i - 1] + 0.5 * k1 * dt, input_signal[i])
        k3 = f(y[i - 1] + 0.5 * k2 * dt, input_signal[i])
        k4 = f(y[i - 1] + k3 * dt, input_signal[i])

        y[i] = y[i - 1] + (1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4) * dt

    return y

def perform_integration_rk4(dataframe, column_to_manipulate, new_columnname, dt=0.5):
    integrated_dataframe = dataframe.copy()
    input_signal = integrated_dataframe[column_to_manipulate].values

    f = lambda y, u: u  # Here, 'u' is the input from 'input_signal'

    output_signal = RK4(f, 0, dt, len(input_signal), input_signal)  # Start from 0

    integrated_dataframe[new_columnname] = output_signal
    return integrated_dataframe



