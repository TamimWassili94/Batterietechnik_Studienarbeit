import tkinter as tk

def open_button2_window(self):
    # Create a new window
    self.button2_window = tk.Toplevel(self.master)
    self.button2_window.title("Button 2 Window")

    # Create some widgets in the new window
    label = tk.Label(self.button2_window, text="This is Button 2's window!")
    button = tk.Button(self.button2_window, text="Close", command=self.button2_window.destroy)

    # Arrange the widgets using grid layout
    label.grid(row=0, column=0, padx=10, pady=10)
    button.grid(row=1, column=0, padx=10, pady=10, sticky="e")
