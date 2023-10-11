import pandas as pd
import os
import glob
import datetime

"""
Need to make seperate functions for reading in the extra dataset that we have available
SolarGIS, Vaisala and SolarAnywhere. Each of these dataset come in in a different format
and need to be setup differently for the API code to function correctly
"""

def read_dataset(data_source, filepath, dataset):
    """
    There are 3 data_source input possibilities, SolarGIS, SolarAnywhere and Vaisala
    :param data_source:
    :param dataset:
    :return:
    """
    # vaisala import function
    # import dataset, set headers, return
    if data_source == "Vaisala":
        df = pd.read_csv(filepath)

        # set datetime column
        df['Datetime'] = pd.to_datetime(df["date time"])
        df = df.set_index('Datetime')
        df = df.rename(
            columns={"GHI (W m-2)": "GHI", "DIF (W m-2)": "DHI", "temperature at 2m (degrees C)": "Tamb",
                     "windspeed at 10m (m s-1)": "Wspd"})
        return df


    # SolarAnywhere import function
    # import dataset(s), set headers, return as single dataset
    if data_source == "SolarAnywhere":
        # Distinction for TMY vs time series
        if dataset == "ts":
            list_of_timeseries = []
            for ts_filepath in os.listdir(f"{filepath}"):
                if ts_filepath.endswith(".csv"):
                    list_of_timeseries.append(ts_filepath)
            # read.csv for each of these into a single dataset
            df = pd.read_csv(os.path.join(filepath, list_of_timeseries[0]), header=1, encoding="windows-1252")
            list_of_timeseries.pop(0)
            for time_series in list_of_timeseries:
                df_toadd = pd.read_csv(os.path.join(filepath, time_series), header=1, encoding="windows-1252")
                df = df.append(df_toadd)
        else:
            df = pd.read_csv(filepath, header=1, encoding="windows-1252")

        df["Datetime"] = df["Date (MM/DD/YYYY)"] +" "+ df["Time (HH:MM)"]
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df = df.set_index('Datetime')
        df = df.rename(
            columns={"Date (MM/DD/YYYY)": "Datetime","GHI (W/m^2)": "GHI", "DHI (W/m^2)": "DHI", "Dry-bulb (C)": "Tamb",
                     "Wspd (m/s)": "Wspd"})

        return df


    # SolarGIS import function
    # todo import dataset, set headers, rebuild datetime, return as single dataset
    if data_source == "SolarGIS":
        if dataset == "tmy":
            df = pd.read_csv(filepath, header=60, sep=";")
            # todo - need to replace day numbers with dates in df for tmy
            df["Date"] = df["Day"].apply(lambda x: datetime.datetime(2003, 1, 1).date() + datetime.timedelta(days=x-1))
            df.Date = df.Date.apply(lambda x: x.strftime("%m/%d/%Y"))
            df["Datetime"] = df["Date"] + " " + df["Time"]
        else:
            df = pd.read_csv(filepath, header=58, sep=";")
            df["Datetime"] = df["Date"] + " " + df["Time"]
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df = df.set_index('Datetime')
        df = df.rename(
            columns={"GHI": "GHI", "DNI": "DHI", "TEMP": "Tamb",
                     "WS": "Wspd"})

        return df

    else: df = False

    return df