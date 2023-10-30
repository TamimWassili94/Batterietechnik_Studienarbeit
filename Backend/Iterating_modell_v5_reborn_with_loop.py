import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Functions_To_Call import plot, lookup_1d, lookup_2d_v2, lookup_2d_v3, integrator
print(f'Funtions_To_Call initialisiert')

from Initial_Parameters import init_volt, init_q_zelle, init_temp, init_soc, kA, cp, m, anzahl_zellen
print(f'Initial_Parameters Initialisiert')

from Time_Tables import (soc_steps_ocv, ocv, temp_steps,
                                R, SOCsteps, R1, C1, R2, C2, DeltaOCVdT, SOCsteps_Takano)
print(f'Time_Tables Initialisiert')

Battery_Dataframe = pd.read_csv('BatteryData_0.csv')
Ladung_Dataframe = pd.read_csv('Charge_Simulink.csv')

# 1. Pre-allocate columns with default values
Battery_Dataframe['Leistung [W]'] = 0
Battery_Dataframe['Current [A]'] = 0
Battery_Dataframe['Charge [C]'] = 0
Battery_Dataframe['SOC [%]'] = init_soc
Battery_Dataframe['U_R1 [V]'] = 0.0
Battery_Dataframe['U_R [V]'] = 0.0
Battery_Dataframe['I_R1 [A]'] = 0.0
Battery_Dataframe['U_R2 [V]'] = 0.0

Battery_Dataframe['I_R2 [A]'] = 0.0
Battery_Dataframe['Q_Irrev [W]'] = 0
Battery_Dataframe["Q_Sum_Cell [W]"] = 0
Battery_Dataframe['U_ges [V]'] = 0.0
Battery_Dataframe.at[0, 'U_ges [V]'] = init_volt
Battery_Dataframe['Temperatur [K]'] = init_temp
Battery_Dataframe['Output Temperature [K]'] = init_temp
Battery_Dataframe.at[0, 'Output Temperature [K]'] = init_temp

# Assuming t is a column in Battery_Dataframe
time = Battery_Dataframe['Zeit [s]']
U_R1_out = np.zeros_like(Battery_Dataframe["Zeit [s]"].values)
ausgangs_temperatur_1 = init_temp
u_zelle = init_volt

end_time = len(time)

for i, row in Battery_Dataframe.iloc[:-1].iterrows():  # Anpassung um Simulink gerecht zu werden
    # Nebenberechnung um den fortschritt der Berechnung anzuzeigen
    progress = (i / end_time) * 100
    print('\rVerarbeitet: {:.2f}%'.format(progress), end='')

    dt = time[i+1] - time[i]  # Zeitschritt zur nächsten Iteration, Differenzial für Integratoren

    # Leistung zum zeitpunkt i aus dem Dataframe (initialisierung in Variable)
    leistung_kw = Battery_Dataframe.at[i, 'Leistung [kW]']  # Ablesen der Leistung aus Dataframe

    # Schritt 1: Umrechnung auf Watt in thermodynamischer konvention (Gain, Multiplikator)
    leistung_w = leistung_kw * -1000  # Gain Block oder Multiplikator
    Battery_Dataframe.at[i, 'Leistung [W]'] = leistung_w  # Einspeisen in das Dataframe

    # Schritt 2: Berechnung des Stroms (Gain, Teiler)
    i_zelle = leistung_w / u_zelle  # Gain Block oder Multiplikator
    Battery_Dataframe.at[i, 'Current [A]'] = i_zelle  # Einspeisen in das Dataframe

    # Schritt 3: Berechnung der Ladung (Integrator)
    q_vorhanden_0 = Battery_Dataframe.at[i, 'Charge [C]']  # Ladung aus Zeitpunkt t
    q_vorhanden_1 = q_vorhanden_0 + i_zelle * dt  # Integratorblock

    # Setzen Sie den berechneten Wert für den nächsten Zeitschritt
    Battery_Dataframe.at[i + 1, 'Charge [C]'] = q_vorhanden_1  # Einspeisen in das Dataframe

    # Schritt 4: Umrechnung der Ladung in SOC
    divident_q_zelle = 1 / init_q_zelle                                         #(initialisieren der Variable)
    stunden_in_sekunden = 1 / 3600                                              #(initialisieren der Variable)
    prozent = 100                                                               #(initialisieren der Variable)
    soc = q_vorhanden_1 * divident_q_zelle * stunden_in_sekunden * prozent      #Drei Gains oder Multiplikator
    soc += init_soc                                                             #Berücksichtigen des initialwerts
    soc = max(0, min(100, soc))                                                 #Saturation Block
    Battery_Dataframe.at[i + 1, 'SOC [%]'] = soc                                    #Einspeisen in das Dataframe

    # Schritt 5: Interpolation der Ohmschen Größen
    # 5.1: 2-D Lookup Interpolation vom OCV [V]
    string_ocv = 'OCV [V]'
    # Aufrufen der Funktion
    interpolated_value = lookup_2d_v3(soc, ausgangs_temperatur_1, soc_steps_ocv, temp_steps, ocv)
    Battery_Dataframe.at[i + 1, string_ocv] = interpolated_value

    # 5.2: 2-D Lookup Interpolation von R [Ohm]
    string_R = 'R [Ohm]'
    # Aufrufen der Funktion
    interpolated_value = lookup_2d_v3(soc, ausgangs_temperatur_1, SOCsteps, temp_steps, R)
    Battery_Dataframe.at[i + 1, string_R] = interpolated_value

    # 5.3: 2-D Lookup Interpolation von R1 [Ohm]
    string_R1 = 'R1 [Ohm]'
    # Aufrufen der Funktion
    interpolated_value = lookup_2d_v3(soc, ausgangs_temperatur_1, SOCsteps, temp_steps, R1)
    Battery_Dataframe.at[i + 1, string_R1] = interpolated_value

    # 5.4: 2-D Lookup Interpolation von R2 [Ohm]
    string_R2 = 'R2 [Ohm]'
    interpolated_value = lookup_2d_v3(soc, ausgangs_temperatur_1, SOCsteps, temp_steps, R2)
    Battery_Dataframe.at[i + 1, string_R2] = interpolated_value

    # 5.5: 2-D Lookup Interpolation von C1 [C]
    string_C1 = 'C1 [C]'
    interpolated_value = lookup_2d_v3(soc, ausgangs_temperatur_1, SOCsteps, temp_steps, C1)
    Battery_Dataframe.at[i + 1, string_C1] = interpolated_value

    # 5.6: 2-D Lookup Interpolation von C2 [C]
    string_C2 = 'C2 [C]'
    interpolated_value = lookup_2d_v3(soc, ausgangs_temperatur_1, SOCsteps, temp_steps, C2)
    Battery_Dataframe.at[i + 1, string_C2] = interpolated_value

    # Schritt 6: Berechnung der Spannung
    # 6.1: Berechnung der Spannung U_R [V]
    r = Battery_Dataframe.at[i + 1, 'R [Ohm]']                                      #(initialisieren der Variable)
    u_r = r * i_zelle                                                           #Gain Block oder Multiplikator
    Battery_Dataframe.at[i + 1, 'U_R [V]'] = u_r                                    #Einspeisen in das Dataframe

    # 6.2: Berechnung von I_R1
    r_1 = Battery_Dataframe.at[i + 1, 'R1 [Ohm]']                                   #(initialisieren der Variable)
    u_r1_prev = Battery_Dataframe.at[i, 'U_R1 [V]']                         #(initialisieren der Variable)
    i_r1 = u_r1_prev / r_1                                                      #Gain Block oder Multiplikator
    Battery_Dataframe.at[i, 'I_R1 [A]'] = i_r1                                  #Einspeisen in das Dataframe

    # 6.2: Berechnen von delta_i_1
    delta_i_1 = i_zelle - i_r1                                                  #Subtract Block

    # 6.3: Berechnung von dU_R_1/dt
    c_1 = Battery_Dataframe.at[i + 1, 'C1 [C]']                                     #(initialisieren der Variable)
    differenzial_u_r1 = delta_i_1 / c_1                                         #Division Block

    # 6.4: Berechnung von Spannung U_R1 über Integrator
    u_r1 = u_r1_prev + differenzial_u_r1 * dt                                   #Integratorblock
    Battery_Dataframe.at[i + 1, 'U_R1 [V]'] = u_r1                                  #Einspeisen in das Dataframe

    # 6.5: Berechnung von I_R2
    r_2 = Battery_Dataframe.at[i + 1, 'R2 [Ohm]']  # (initialisieren der Variable)
    u_r2_prev = Battery_Dataframe.at[i, 'U_R2 [V]']  # (initialisieren der Variable)
    i_r2 = u_r2_prev / r_2  # Gain Block oder Multiplikator
    Battery_Dataframe.at[i, 'I_R2 [A]'] = i_r2  # Einspeisen in das Dataframe

    # 6.6: Berechnen von delta_i_2
    delta_i_2 = i_zelle - i_r2  # Subtract Block

    # 6.7: Berechnung von dU_R_2/dt
    c_2 = Battery_Dataframe.at[i + 1, 'C2 [C]']  # (initialisieren der Variable)
    differenzial_u_r2 = delta_i_2 / c_2  # Division Block

    # 6.8: Berechnung von Spannung U_R2 über Integrator
    u_r2 = u_r2_prev + differenzial_u_r2 * dt  # Integratorblock
    Battery_Dataframe.at[i + 1, 'U_R2 [V]'] = u_r2  # Einspeisen in das Dataframe

    # 6.9 Berechnung der gesamten Zellspannung
    u_zelle = (
            Battery_Dataframe.at[i + 1, 'U_R1 [V]'] +
            Battery_Dataframe.at[i + 1, 'U_R2 [V]'] +
            Battery_Dataframe.at[i + 1, 'U_R [V]'] +
            Battery_Dataframe.at[i + 1, 'OCV [V]']
    ) * anzahl_zellen                                                           #Add Block

    Battery_Dataframe.at[i + 1, 'U_ges [V]'] = u_zelle                              #Einspeisen in das Dataframe

    # Schritt 7: Berechnung der irreversiblen Wärme
    # 7.1: Berechnung der irreversiblen Wärme der ohmschen Größen
    q_r = r * (i_zelle ** 2)  # Gain Block oder Multiplikator
    q_r1 = r_1 * (i_r1 ** 2)  # Gain Block oder Multiplikator
    q_r2 = r_2 * (i_r2 ** 2)  # Gain Block oder Multiplikator

    # 7.2: Berechnung der irreversiblen Wärme
    q_irreversibel = q_r + q_r1 + q_r2  # Add Block
    Battery_Dataframe.at[i + 1, 'Q_Irreversibel [W]'] = q_irreversibel  # Einspeisen in das Dataframe

    # Schritt 8: Berechnung von reversibler Wärme
    delta_ocv = lookup_1d(soc, SOCsteps_Takano, DeltaOCVdT)  # Nutzung von 1-D Lookup Table
    Battery_Dataframe.at[i + 1, "Delta OCV [V]"] = delta_ocv  # Einspeisen in das Dataframe
    ist_temperatur = Battery_Dataframe.at[i + 1, 'Temperatur [K]']  # Auslesen der ist-Temperatur
    q_reversibel = ist_temperatur * i_zelle * delta_ocv  # Gain Block oder Multiplikator
    Battery_Dataframe.at[i + 1, "Q_Reversibel [W]"] = q_reversibel  # Einspeisen in das Dataframe

    # Schritt 9: Berechnung von Zellwärme als Summe und einzeln
    q_zelle = q_reversibel + q_irreversibel  # Add Block
    Battery_Dataframe.at[i + 1, "Q_Cell [W]"] = q_zelle  # Einspeisen in das Dataframe

    q_zelle_summe = anzahl_zellen * q_zelle  # Gain Block oder Multiplikator
    Battery_Dataframe.at[i + 1, "Q_Sum_Cell [W]"] = q_zelle_summe  # Einspeisen in das Dataframe

    # Schritt 10: Berechnung der Temperatur (Siehe Abschnitt Schmidt Bat Lab. Aufgabenstellung)
    delta_temperatur = ist_temperatur - ausgangs_temperatur_1  # Substract Block
    q_kuehlung_negativ = kA * delta_temperatur  # Negativ thermodynamische konvention
    sum_q = q_kuehlung_negativ + q_zelle  # Summe der Wärme
    d_temperatur = sum_q / (m * cp)  # Berechnung des temperatur differenzials
    ausgangs_temperatur_0 = Battery_Dataframe.at[i , 'Output Temperature [K]']  # Temperatur aus letzter iteration
    ausgangs_temperatur_1 = ausgangs_temperatur_0 + d_temperatur * dt  # Integrator Block

    # Store this "output" temperature
    Battery_Dataframe.at[i + 1, 'Output Temperature [K]'] = ausgangs_temperatur_1  # Einspeisen in das Dataframe



print('\nSimulation abgeschlossen!')


#Battery_Dataframe = Battery_Dataframe.drop(Battery_Dataframe.index[-1])

print(len(Battery_Dataframe))

Time = Battery_Dataframe['Zeit [s]']
Ladung_Dataframe_Simulink = Ladung_Dataframe['0']
Ladung_Dataframe_Python = Battery_Dataframe['Charge [C]']
error = Ladung_Dataframe_Simulink - Ladung_Dataframe_Python
plt.plot(Time, error)
plt.show()

plot(Battery_Dataframe, "Zeit [s]", 'OCV [V]')
plot(Battery_Dataframe, "Zeit [s]", 'U_R [V]')
plot(Battery_Dataframe, "Zeit [s]", 'I_R1 [A]')
plot(Battery_Dataframe, "Zeit [s]", 'U_R1 [V]')
plot(Battery_Dataframe, "Zeit [s]", 'U_R2 [V]')
plot(Battery_Dataframe, "Zeit [s]", 'I_R2 [A]')
plot(Battery_Dataframe.iloc[22:28], "Zeit [s]", 'U_ges [V]')
plot(Battery_Dataframe, "Zeit [s]", 'Output Temperature [K]')
#plot(Battery_Dataframe, "Zeit [s]", "Q_Irreversibel [W]")
#plot(Battery_Dataframe, "Zeit [s]", "Q_Reversibel [W]")
#plot(Battery_Dataframe.head(30), "Zeit [s]", "Q_Sum_Cell [W]")