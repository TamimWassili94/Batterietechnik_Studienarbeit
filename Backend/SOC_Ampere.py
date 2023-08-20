import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal

from Matlab_dotmat_reader import df,x_title,y_title,plot_dataframe
from transfer_functions import perform_integration

def kilowatt_to_watt_and_reverse(dataframe,y_coloumn): ##Works
    new_dataframe = dataframe.copy()
    new_column_name = f"Leistung [W]"
    new_dataframe[new_column_name] = new_dataframe[y_coloumn] / -1000
    return new_dataframe

def watt_to_ampere(dataframe, voltage):
    ampere_dataframe = dataframe.copy()
    new_column_name = f"Strom [A]"
    ampere_dataframe[new_column_name] = ampere_dataframe.iloc[:, 1] / voltage
    return ampere_dataframe


watt_dataframe = kilowatt_to_watt_and_reverse(df,y_title)
ampere = watt_to_ampere(watt_dataframe,2.4)
ladungsmenge_t = perform_integration(ampere, "Strom [A]" , "Ladungsmenge[t]")


plot_dataframe(watt_dataframe,watt_dataframe.columns[0],watt_dataframe.columns[2])
plot_dataframe(ampere,ampere.columns[0],ampere.columns[3])
plot_dataframe(ladungsmenge_t,ladungsmenge_t.columns[0],ladungsmenge_t.columns[4])