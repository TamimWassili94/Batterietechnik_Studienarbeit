import scipy.io
import pandas as pd
import h5py
import os
import matplotlib.pyplot as plt


def dotmatloader(dateiname):
    scipydata = scipy.io.loadmat(dateiname)
    return scipydata

def scipytopandasconverter(scipydata):
    dataframe = pd.DataFrame(scipydata['A'])
    dataframe = dataframe.rename(index={0: 'Zeit [s]', 1: 'Leistung [kW]'})
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

def get_axis_titles(dataframe):
    x_axis_title = dataframe.columns[0]  # Assuming the first column is the x-axis
    y_axis_title = dataframe.columns[1]  # Assuming the second column is the y-axis
    return x_axis_title,y_axis_title

    return x_axis_title, y_axis_title
def plot_dataframe(dataframe, x_column, y_column):

    plt.plot(dataframe[x_column], dataframe[y_column])
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f'Scatter Plot: {x_column} vs {y_column}')
    plt.show()


# testen der angegebenen Funktionen - erfolgreich in klammer dateinamen eingeben des profils
# Das profil muss im gleichen ordner sein wie die .py dateien.
Battery_Dataframe = dotmat_to_pandas("Profile_1.mat")
x_title,y_title = get_axis_titles(Battery_Dataframe)

# .pys arbeiten indem sie das Datafram von .csv ablesen
Battery_Dataframe.to_csv('BatteryData_0.csv', index=False)


