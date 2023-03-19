import tkinter as tk
from tkinter import ttk
from button_1 import open_file_selector

class Main_Menu:
    def __init__(self, master):
        self.master = master
        master.title("Main Menu")

        # Create buttons and assign them to a function
        self.button1 = tk.Button(master, text="Import Data", command=lambda: open_file_selector(
            self.button2, self.button3, self.button4, self.button5, self.button6, self.treeview)
                                 )
        self.button2 = tk.Button(master, text="Button 2", command=self.do_something, state=tk.DISABLED)
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

        # Create a frame to hold the treeview
        self.frame = tk.Frame(master)
        self.frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Create Treeview widget
        self.treeview = ttk.Treeview(master, columns=("col1", "col2"))
        self.treeview.heading("#0", text="Index")
        self.treeview.heading("col1", text="Zeit [s]")
        self.treeview.heading("col2", text="Leistung [W]")
        self.treeview.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.treeview.grid_remove()

        # Create error label and hide it
        self.error_label = tk.Label(master,
                                    text="Error 03: No file has been selected. Please import a file in a supported file format.",
                                    fg="red")
        self.error_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.error_label.grid_remove()

        # Add vertical scrollbar to the treeview
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.treeview.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Arrange the treeview and scrollbar using grid layout
        scrollbar.grid(row=3, column=2, padx=10, pady=10, sticky="ns")
        self.master.grid_columnconfigure(2, weight=1)

        # Configure rows and columns to expand with the window
        for i in range(3):
            self.master.grid_rowconfigure(i, weight=1)
        self.master.grid_rowconfigure(3, weight=3)  # make the row with the treeview expand more

        # Configure rows and columns to expand with the window
        for i in range(3):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.master.grid_columnconfigure(i, weight=1)

    def do_something(self):
        print("Button pressed!")


root = tk.Tk()
main_menu = Main_Menu(root)
root.mainloop()
