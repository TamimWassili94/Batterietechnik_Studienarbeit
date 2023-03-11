# Batterietechnik_Studienarbeit
ENTWICKLUNG EINES PYTHON-BASIERTEN LI-IONEN BATTERIEMODELLS

Das Verhalten von Batterien wird für die Systemanforderung, oftmals durch Ersatzmodelle 
modelliert. Diese Modelle erlauben die Berechnung von dynamischen Lastfällen
Im Modul Batterietechnik ist die Simulation des Batterieverhaltens ein wichtiges Werkzeug, um 
die Ersatzmodelle einer Batterie im Vergleich zum tatsächlichen Verhalten einer Batterie 
validieren zu können. Ziel ist es das bestehende Simulink Modell in einem Python-Code 
umzusetzen. Es gelten die gleichen Anforderungen wie für das Simulink-Programm.

Das zu erzeugende Programm sollte daher folgende Anforderungen/ Funktionen beinhalten:
- Umsetzung in Python
- Berechnung des instationären elektrischen und thermischen Verhaltens
- Erweiterbarkeit hinsichtlich Systemarchitektur
o Elektrische Verschaltung (nsmp)
o Schnittstelle zu Fahrzeug-Thermomanagement
- Gleiche Funktionalität wie bestehendes Simulink-Modell
- Möglichkeit zum Einlesen von testbasierten Fahrzyklen
- Geeignetes grafisches Interface zur Dateneingabe
Die Arbeit ist schriftlich so zu dokumentieren, dass sie als Laborskript für zukünftige 
Veranstaltungen in Batterietechnik eingesetzt werden kann.