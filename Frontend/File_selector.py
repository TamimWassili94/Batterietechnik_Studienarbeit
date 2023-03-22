import tkinter as tk
from tkinter import ttk
from button_1_data import open_file_selector
from button_2_plot import open_plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class MainMenu:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Menu")

        # Create buttons and assign them to a function
        self.button1 = tk.Button(master, text="Import Data", command=lambda: open_file_selector(self))
        self.button2 = tk.Button(master, text="Button 2", command=self.open_plot)
        self.button3 = tk.Button(master, text="Button 3", command=self.do_something, state=tk.DISABLED)
        self.button4 = tk.Button(master, text="Button 4", command=self.do_something, state=tk.DISABLED)
        self.button5 = tk.Button(master, text="Button 5", command=self.do_something, state=tk.DISABLED)
        self.button6 = tk.Button(master, text="Button 6", command=self.do_something, state=tk.DISABLED)

        # Arrange the buttons using grid layout
        self.button1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.button2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.button3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.button4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.button5.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.button6.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # Create Treeview widget
        self.treeview = ttk.Treeview(master, columns=("col1", "col2"))
        self.treeview.heading("#0", text="Index")
        self.treeview.heading("col1", text="Zeit [s]")
        self.treeview.heading("col2", text="Leistung [W]")
        self.treeview.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Add vertical scrollbar to the treeview
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.treeview.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Configure rows and columns to expand with the window
        for i in range(4):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.master.grid_columnconfigure(i, weight=1)

    def do_something(self):
        print("Button pressed!")

    def open_plot(self):
        # Get the data from Button 1
        data = self.button1.dataframe

        # Create a figure and plot the data
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(data["Zeit [s]"], data["Leistung [W]"], linewidth=0.5)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
        ax.set_xlabel("Zeit [s]")
        ax.set_ylabel("Leistung [W]")

        # Create a canvas to display the plot in the main menu window
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=3, column=3, rowspan=3, padx=10, pady=10, sticky="nsew")

        # Add a toolbar with a zoom button to the plot window
        toolbar_frame = tk.Frame(self.master)
        toolbar_frame.grid(row=3, column=3, padx=0, pady=0, sticky="e")
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        self.canvas.get_tk_widget().grid(row=0, column=3)


root = tk.Tk()
main_menu = MainMenu(root)
root.mainloop()
