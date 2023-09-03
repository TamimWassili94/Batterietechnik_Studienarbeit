from Matlab_dotmat_reader import df,x_title,y_title,plot_dataframe
from transfer_functions import perform_integration
from Initial_Parameters import q_zelle, soc_init

def kilowatt_to_watt_and_reverse(dataframe,y_coloumn): ##Works
    new_dataframe = dataframe.copy()
    new_column_name = f"Leistung [W]"
    new_dataframe[new_column_name] = new_dataframe[y_coloumn] * -1000
    return new_dataframe

def watt_to_ampere(dataframe, voltage):
    ampere_dataframe = dataframe.copy()
    new_column_name = f"Strom [A]"
    ampere_dataframe[new_column_name] = ampere_dataframe["Leistung [W]"] / voltage
    return ampere_dataframe

def current_SOC(dataframe, q_max, initial_soc):
    constant_by_time = 100/(3600*q_max)
    soc_dataframe = dataframe.copy()
    soc_dataframe["SOC [%]"] = (initial_soc + soc_dataframe["Ladungsmenge[t]"]*constant_by_time).clip(0,100)
    return soc_dataframe

watt_dataframe = kilowatt_to_watt_and_reverse(df,y_title)
ampere = watt_to_ampere(watt_dataframe, 45)
ladungsmenge_t = perform_integration(ampere, "Strom [A]" , "Ladungsmenge[t]")
soc = current_SOC(ladungsmenge_t, q_zelle, soc_init)

#plot_dataframe(watt_dataframe,watt_dataframe.columns[0],watt_dataframe.columns[1]) #check
#plot_dataframe(watt_dataframe,watt_dataframe.columns[0],watt_dataframe.columns[2]) #check
#plot_dataframe(ampere,ampere.columns[0],ampere.columns[3])
#plot_dataframe(ladungsmenge_t,ladungsmenge_t.columns[0],ladungsmenge_t.columns[4])
plot_dataframe(soc, soc.columns[0], soc.columns[5])

soc.to_csv('BatteryData_1.csv', index=False)