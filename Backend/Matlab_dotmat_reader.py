import scipy.io
import pandas as pd
import h5py
import os
from tkinter import filedialog
from tkinter import Tk

def dotmatloader(dateiname):
    scipydata = scipy.io.loadmat(dateiname)
    return scipydata

def scipytopandasconverter(scipydata):
    dataframe = pd.DataFrame(scipydata['A'])
    dataframe = dataframe.rename(index={0: 'Zeit [s]', 1: 'Leistung [W]'})
    dataframe = dataframe.transpose()
    return dataframe

def mat_to_csv(dateiname):
    root = Tk()
    root.withdraw()
    output_filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    root.destroy()

    if not output_filename:
        print("No output file selected.")
        return None

    with h5py.File(dateiname, 'r') as file:
        for key in file.keys():
            if isinstance(file[key], h5py.Dataset):
                data = file[key][()]
                data = pd.DataFrame(data)
                data.to_csv(output_filename, index=False)
    return output_filename

def dotmat_to_pandas(dateiname):
    _, file_extension = os.path.splitext(dateiname)

    if file_extension.lower() == ".mat":
        try:
            scipydata = dotmatloader(dateiname)
            dataframe = scipytopandasconverter(scipydata)
        except NotImplementedError:
            output_csv_filename = mat_to_csv(dateiname)
            if output_csv_filename:
                print(f"Conversion to DataFrame failed. Data saved as a CSV file: {output_csv_filename}")
            else:
                print("Conversion to DataFrame failed and no CSV file was saved.")
            raise
    elif file_extension.lower() == ".csv":
        dataframe = pd.read_csv(dateiname)
    else:
        raise ValueError(f"Unsupported file format '{file_extension}'. Please provide a .mat or .csv file.")

    return dataframe


# testen der angegebenen Funktionen - erfolgreich
# df = dotmat_to_pandas("Profile_1.mat")
# print(df)
# print("Column names:", list(df.columns))
