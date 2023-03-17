import tkinter as tk

class Mainmenu(tk.Frame):
    def __init__(self, master=None, df=None):
        super().__init__(master)
        self.master = master
        self.master.title("Main Menu")
        self.master.state('zoomed')  # Maximize the window
        self.pack()
        self.create_widgets(df)

    def create_widgets(self, df):
        # create widgets using the `df` variable
        pass # Add your widgets here

