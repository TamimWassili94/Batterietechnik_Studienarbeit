from tkinter import filedialog
import tkinter as tk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Backend')))
import Matlab_dotmat_reader


def open_file_selector(mainmenu_instance):
    button1,button2, button3, button4, button5, button6, treeview = mainmenu_instance.button1,\
        mainmenu_instance.button2, \
        mainmenu_instance.button3, \
        mainmenu_instance.button4, \
        mainmenu_instance.button5, \
        mainmenu_instance.button6, \
        mainmenu_instance.treeview

    filetypes = [("CSV files", "*.csv"), ("MAT files", "*.mat"), ("All files", "*.*")]
    filepath = filedialog.askopenfilename(title="Select a file", filetypes=filetypes)
    if filepath:
        button2.config(state=tk.NORMAL)
        button3.config(state=tk.NORMAL)
        button4.config(state=tk.NORMAL)
        button5.config(state=tk.NORMAL)
        button6.config(state=tk.NORMAL)
        # Outside the class
        show_treeview = True

        for item in treeview.get_children():
            treeview.delete(item)

        if show_treeview:
            treeview.grid()
        else:
            treeview.grid_remove()
        print("Selected file:", filepath)
        # Load the data using the dotmat_to_pandas function
        data = Matlab_dotmat_reader.dotmat_to_pandas(filepath)

        # assuming you have loaded your data into a pandas DataFrame called "data"
        for i, row in data.iterrows():
            # insert the row index as the first column
            treeview.insert("", "end", text=i, values=(row["Zeit [s]"], row["Leistung [W]"]))



        print("Data loaded:", data)
    else:
        print("No file selected")
        button2.config(state=tk.DISABLED)
        button3.config(state=tk.DISABLED)
        button4.config(state=tk.DISABLED)
        button5.config(state=tk.DISABLED)
        button6.config(state=tk.DISABLED)

    mainmenu_instance.button1.dataframe = data
    print(mainmenu_instance.button1.dataframe)


