"""Diese Datei dient der implementierung von Funktionen in Sympy, die für komplexe Ableitungs und Integraloperationen
verwendet werden kann. Sympy ist auf symbolische berechnungen spezialisiert.

sympy.integrals ist das Modul was für die Laplace transformation konkret benötigt wird.

Im File können auch schon Funktionen im Zeitbereich konvertiert werden und werden in ein Numpy array ausgedrückt und
anschließend in ein Pandas Dataframe gepackt um tabellenartige analyse zu ermöglichen, oder es später in ein Plot zu
übergeben. Geplant ist vielleicht die Aufsplittung zwischen Numpy und Scypy-operationen
"""
import pandas as pd
import sympy as sp
import numpy as np
from sympy.integrals.transforms import laplace_transform


"""sympy_variable_aus_input interprestiert variablen wie die euler zahl oder pi um diese dann in sympy form 
für maschinenverarbeitung zu überführen."""
def simpy_variable_aus_input(input_variable):
    # Interpretiere mathematische Variablen in SymPy-Symbole
    sp.sympify(input_variable, {'e': sp.E, 'pi': sp.pi, 'exp': sp.exp, 'sqrt' : sp.sqrt, 'I': sp.I})
    # Ersetze "^" durch "**"
    input_variable = input_variable.replace('^', '**')


"""In sympy_func_aus_input wird eine mathematische sympy funktion aus einem input heraus interpretiert
um funktionen im Zeitbereich zu ermöglichen. Komplexe Formen sind hier auch möglich."""
def sympy_func_aus_input(input_variable):
    try:
        # Verwende die Funktion sympy_var_from_inputs, um die Variablen zu interpretieren
        s = simpy_variable_aus_input(input_variable)
        # SymPy-Symbol für die unabhängige Variable
        x = sp.symbols('x')
        # Versuche, den Eingabestring als SymPy-Ausdruck auszuwerten
        f = sp.sympify(input_variable)
        # Prüfe, ob der Ausdruck eine Funktion von x ist
        if isinstance(f, sp.Expr) and x in f.free_symbols:
            return sp.lambdify(x, f, 'numpy')  # Erstelle eine SymPy-Funktion
        else:
            raise ValueError("Der Ausdruck ist keine Funktion von x.")
    except:
        # Wenn die Auswertung fehlschlägt, gebe eine Fehlermeldung aus
        raise ValueError("Error 0: Ungültige Eingabe: " + input_variable +
        "\nBitte eines der offiziellen Symbole verwenden:"
        "\ne & exp := Euler-Zahl"
        "\npi := Pi"
        "\n^ & ** für Exponent"
        "\nsqrt() für Wurzel")


"""Führt funktion in einem Zeitbereich aus."""
def zeitbereich_der_funktion_als_numpy_array(input_funktion, von_bis, step):
    t_val = np.arange(von_bis[0], von_bis[1]+step, step)
    f_val = np.array([input_funktion(t_value) for t_value in t_val])
    return t_val, f_val


"""Konvertiert ein numpy Zeitfunktion in ein Pandas Array mit beschriftung"""
def numpy_zeitfunktion_zu_pandas(numpy_array):
    dataframe = pd.DataFrame(numpy_array)
    dataframe = dataframe.rename(index={0: 'Zeit [s]', 1: 'Leistung [W]'})
    return dataframe


"""Test Verwendung - erfolgreich"""
"""Beispielfunktion A"""
f_str = "(x**3 + exp(-2) - sqrt(-2) + 2*I)/33*I"
f = sympy_func_aus_input(f_str)

"""Beispielfunktion B als Eingabe im String (Buchstabenbereich)"""
#f_str = "x**2"
#f = sympy_func_aus_input(f_str)

"""Beispielfunktion C als Errorausgabe"""
#f_str = "expontent(2)"
#f = sympy_func_aus_input(f_str)


# Zeitbereich, in dem die Funktion aufgebaut werden soll, samt timestep.
von_bis = (-5,5)
timestep = 1
f_t = zeitbereich_der_funktion_als_numpy_array(f,von_bis,timestep)

# Konvertierung von Numpy Array in Pandas Dataframe.
dataframe = numpy_zeitfunktion_zu_pandas(f_t)
print(dataframe)