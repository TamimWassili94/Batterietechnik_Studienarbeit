"""Initialparameter"""
anzahl_zellen = 13                  #[-]
init_volt = 3.6 * anzahl_zellen     #[V]        Initialspannung der Batterie
init_soc = 50                       #[%]        Inital State of Charge
init_q_zelle = 5.6                  #[Ah]       Ladungsmenge einer Zelle
init_temp = 293.15                  #[K]        Initaltemperatur
m = 0.2147                          #[kg]       Masse einer Zelle
cp = 800                            #[J/kg K]   Spezifische Wärmekapazität einer Zelle
kA = 1.5                            #[W/K]      Wärmeübergangskoeffizient multipliziert mit der
                                    #           leitenden Oberfläche

