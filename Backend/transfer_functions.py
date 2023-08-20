import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal

def perform_integration(dataframe, column_to_manipulate, new_columnname):
    integrated_dataframe = dataframe.copy()
    input_signal = integrated_dataframe[column_to_manipulate].values

    # Use the trapezoidal rule for integration
    output_signal = np.cumsum(input_signal)
    output_signal -= output_signal[0]  # remove the integration constant if needed

    integrated_dataframe[new_columnname] = output_signal
    return integrated_dataframe