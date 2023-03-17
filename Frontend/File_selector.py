import sys
sys.path.append('C:/Users/Tamim/PycharmProjects/Batterietechnik_Studienarbeit/Backend')

import tkinter as tk
from tkinter import filedialog, messagebox
from main_menu import Mainmenu
from Matlab_dotmat_reader import dotmat_to_pandas

class Fileselector(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("File Chooser")
        self.master.geometry("{0}x{1}+0+0".format(self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        button_width = self.master.winfo_screenwidth() // 4
        button_height = self.master.winfo_screenheight() // 6
        font_size = min(button_width, button_height) // 8

        self.choose_file_button = tk.Button(self, width=button_width, height=button_height, font=("Arial", font_size))
        self.choose_file_button["text"] = "Choose File"
        self.choose_file_button["command"] = self.choose_file
        self.choose_file_button.pack(expand=True)

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("MAT files", "*.mat"), ("CSV files", "*.csv")])
        print("Selected file:", file_path)
        if file_path:
            if not file_path.endswith('.mat') and not file_path.endswith('.csv'):
                messagebox.showerror("Error 02", "Ungültiges Dateiformat. Bitte wählen Sie eine .mat- oder .csv-Datei aus.")
                return
            # Laden der Datei in pandas
            df = dotmat_to_pandas(file_path)
            # Mainscreen initialisieren und pandas dataframe übergeben
            main_menu_window = tk.Toplevel(self.master)
            main_menu_window.title("Main Screen")
            main_menu_window.attributes("-fullscreen", True)  # Open the main screen in fullscreen mode
            Mainmenu(main_menu_window, df)
            self.master.destroy()  # Close the file chooser window


root = tk.Tk()
root.state('zoomed')
app = Fileselector(master=root)
app.mainloop()
