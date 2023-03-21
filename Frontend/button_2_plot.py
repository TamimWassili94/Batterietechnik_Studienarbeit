# button_2_plot.py

import matplotlib.pyplot as plt

def open_plot(data):
    # Create plot using data
    plt.plot(data['Zeit [s]'], data['Leistung [W]'])
    plt.xlabel('Zeit [s]')
    plt.ylabel('Leistung [W]')
    plt.title('Plot of Data')

    # Display plot in new window
    plt.show()