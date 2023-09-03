import numpy as np

soc_init = 40
q_zelle = 5.6 #[Ah]
I_ZELLE = -1 #[A]
Temperature = 298.15 #[K]
Steptime = 1

# SOC steps [%]
SOCsteps = np.arange(30, 71, 10)
soc_steps_ocv = np.arange(0,101,10)

# Temperaturschritte [K]
temp_steps = np.array([253.15, 263.15, 283.15, 298.15, 313.15, 323.15])

# Open circuit voltage [V] OCV(SOC,T) mit Reihe (Tsteps) und Spalte (SOCsteps_OCV)
ocv_pre_vector = np.array([3.3383, 3.4305, 3.5207, 3.5875, 3.6381, 3.7006, 3.7786, 3.8741, 3.9564, 4.0601, 4.1651])
ocv = np.tile(ocv_pre_vector, (len(temp_steps), 1))

# Kapazität
KAPtotal = 4.75

# Ohmscher Widerstand R
R_values = np.array([0.015456, 0.008921403, 0.003025827, 0.00178, 0.0013081, 0.0011997])
R = np.outer(R_values, np.ones(len(SOCsteps)))

print(R)
print(R_values)

# Ohmscher Widerstand R1
R1_flat = np.array([
    0.003438371, 0.002916329, 0.002500086, 0.003006543, 0.002435014,
    0.002858014, 0.001729457, 0.001255586, 0.000980971, 0.000816457,
    0.001474333, 0.001820375, 0.0013482, 0.001349767, 0.0016597,
    0.00147666, 0.00172252, 0.00133324, 0.00108482, 0.00122998,
    0.000877257, 0.000836543, 0.000662386, 0.000611971, 0.000574529,
    0.000733214, 0.000687786, 0.000560757, 0.000530671, 0.000526186
])

# Reshape to 6x5 matrix
R1 = R1_flat.reshape((6, 5))

# Kapazität C1
C1 = np.array([
    [74.07342857, 77.83357143, 69.622, 55.87042857, 60.53857143],
    [286.3941429, 660.9157143, 931.9482857, 872.1554286, 1078.943714],
    [5420.817, 9287.1545, 6727.824667, 7934.770667, 14827.54133],
    [8847.9084, 11108.3464, 9550.6452, 11591.2628, 9428.2788],
    [6735.832571, 7316.534857, 6798.601429, 7224.155286, 8773.502571],
    [6199.531429, 6119.823143, 6281.261143, 8212.094, 9745.440571]
])

# Ohmscher Widerstand R2
R2 = np.array([
    [0.008776371, 0.006872929, 0.007282371, 0.0077283, 0.006168],
    [0.0083573, 0.006514429, 0.006704257, 0.004338714, 0.002015429],
    [0.0019077, 0.001436825, 0.0016947, 0.0016471, 0.001013233],
    [0.00124686, 0.0009181, 0.00110466, 0.00111646, 0.00128264],
    [0.001085071, 0.001098714, 0.001094271, 0.001083786, 0.001044357],
    [0.001074429, 0.0010991, 0.001066529, 0.0010419, 0.001026757]
])

# Kapazität C2
C2 = np.array([
    [2501.824714, 4851.367714, 6117.925857, 5847.742857, 6737.781286],
    [3378.918857, 5195.220857, 9283.824143, 11465.34029, 12217.21114],
    [6187.002, 5879.76225, 8847.052333, 11166.68067, 4026.341667],
    [7314.3228, 8227.8342, 9585.0106, 9738.4632, 10633.793],
    [11986.68714, 14554.9, 15085.47214, 16225.34971, 16864.36214],
    [13622.89557, 14469.22614, 14751.22386, 14856.81671, 14909.39914]
])

# Reversible Wärmefreisetzung dOCV/dt(SOC) [V/K]
SOCsteps_Takano = np.arange(0, 101, 5)
DeltaOCVdT = 1e-3 * np.array([-0.06, -0.2, -0.3, -0.35, -0.25, -0.2, -0.145, -0.11, -0.1, 0,
                              0.05, 0.1, 0.19, 0.15, 0.12, 0.1, 0.05, 0.05, 0.05, 0.025, 0])


# Check shapes
shape_R1 = R1.shape
shape_C1 = C1.shape
shape_R2 = R2.shape
shape_C2 = C2.shape

print(f"Shape of R1: {shape_R1}")
print(f"Shape of C1: {shape_C1}")
print(f"Shape of R2: {shape_R2}")
print(f"Shape of C2: {shape_C2}")


# Thermische Parameter
m = 0.2147
cp = 800
kA = 1.5

# Parameter eigene
V_max = 0.00178571
T_w_ein = 298.15
Area = 0.0096
Width = 0.01
Length = 0.12
Height = 0.08