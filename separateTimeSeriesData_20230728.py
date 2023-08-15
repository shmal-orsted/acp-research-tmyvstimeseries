import pandas as pd
import os
import Optimization.main as op

cwd = os.getcwd()
filename = "ElevenMile_TimeSeries_ACP__20230728.csv"
filepath = os.path.join(cwd, "Data", "ElevenMile", filename)
df = pd.read_csv(filepath)
# print(df)


# todo seperate years from the solar data
df['Datetime'] = pd.to_datetime(df["date time"])
df = df.set_index('Datetime')

# get list of unique years from dataframe
list_of_years = list(df.index.year.unique())

# make dict of years with df for each year
d = {}

for year in list_of_years:
    d[year] = df.loc[f"{year}-1-1":f"{year}-12-31"]

# TODO implement optimization
json_list = []
json_dict = {}


# Manually enter GCR and AC/DC ratio and ACCapacity
gcr = 35  # percentage
acdc = 1.3  # eg: 1.3
ac = 100000
d_list = d.keys()


# TODO iterate through all years later

for i in d_list:
    year = i
    try:
        json_dict[year] = (op.main(d[i], gcr, acdc, year, ac))
    except:
        json_dict[year] = []

pass