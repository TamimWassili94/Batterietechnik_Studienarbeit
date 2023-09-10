from Matlab_dotmat_reader import df,x_title,y_title,plot_dataframe
from transfer_functions import perform_integration_rk4
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

Battery_Dataframe = kilowatt_to_watt_and_reverse(df,y_title)
Battery_Dataframe = watt_to_ampere(Battery_Dataframe, 45)
Battery_Dataframe = perform_integration_rk4(Battery_Dataframe, "Strom [A]" , "Ladungsmenge[t]")
Battery_Dataframe = current_SOC(Battery_Dataframe, q_zelle, soc_init)

#plot_dataframe(watt_dataframe,watt_dataframe.columns[0],watt_dataframe.columns[1]) #check
#plot_dataframe(watt_dataframe,watt_dataframe.columns[0],watt_dataframe.columns[2]) #check
plot_dataframe(Battery_Dataframe,Battery_Dataframe.columns[0],Battery_Dataframe.columns[3])
plot_dataframe(Battery_Dataframe,Battery_Dataframe.columns[0],Battery_Dataframe.columns[4])
#plot_dataframe(Battery_Dataframe, Battery_Dataframe.columns[0], Battery_Dataframe.columns[5])

Battery_Dataframe.to_csv('BatteryData_1.csv', index=False)