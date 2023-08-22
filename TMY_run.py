import json
import pandas as pd
import os
import Optimization.main as op
import numpy as np

cwd = os.getcwd()
filename = "ElevenMile_TMY_ACP__20230728.csv"
filepath = os.path.join(cwd, "Data", "ElevenMile", filename)
df = pd.read_csv(filepath, header=11)
# print(df)

# todo seperate years from the solar data
df['Datetime'] = pd.to_datetime(df["date time"])
df = df.set_index('Datetime')

# TODO implement optimization
json_list = []
json_dict = {}


# Manually enter GCR and AC/DC ratio and ACCapacity
gcr = 35  # percentage
acdc = 1.3  # eg: 1.3
ac = 100000

year = "TMY"

# load a file if one does not exist
try:
    # check if there is a file to read first
    with open("json_dict_storage_TMY.json", "r") as openfile:
        # read the json file
        json_dict = json.load(openfile)
except FileNotFoundError:
    # TODO iterate through all years later
        json_dict = (op.main(df, gcr, acdc, year, ac))


json_object = json.dumps(json_dict, indent=4)

# write the json to a file for storage
with open("json_dict_storage_TMY.json", "w") as outfile:
    outfile.write(json_object)

# Make a list of the p50 values from SRC
list_of_p50s = []


# add those p50 to a dataframe
try:
    list_of_p50s.append(json_dict[year]["SummaryAnnual"]["netEnergy"])
except TypeError:
    list_of_p50s.append(np.NaN)
except KeyError:
    try:
        list_of_p50s.append(json_dict[str(year)]["SummaryAnnual"]["netEnergy"])
    except KeyError:
        list_of_p50s.append(np.NaN)
    except TypeError:
        list_of_p50s.append(np.NaN)

# get the mean p50 from the src runs
df_of_p50s = pd.DataFrame(list_of_p50s)
df_of_p50s.to_csv("p50s_export_TMY.csv")  # export p50s to csv file
dataset_p50 = df_of_p50s.mean()

list_of_hourly_dfs = []

# make 8760 dataset output
try:
    list_of_hourly_dfs.append(pd.DataFrame(json_dict[year]["Hourly"]).swapaxes("index", "columns")["E_Grid"])
except TypeError:
    list_of_hourly_dfs.append(pd.DataFrame(data=[(0)], columns=["E_Grid"]))
except KeyError:
    try:
        list_of_hourly_dfs.append(pd.DataFrame(json_dict[str(year)]["Hourly"]).swapaxes("index", "columns")["E_Grid"])
    except KeyError:
        list_of_hourly_dfs.append(pd.DataFrame(data=[(0)], columns=["E_Grid"]))
    except TypeError:
        list_of_hourly_dfs.append(pd.DataFrame(data=[(0)], columns=["E_Grid"]))

hourly_dfs = pd.concat(list_of_hourly_dfs, axis=1)
hourly_dfs.to_csv("8760_exports_TMY.csv")

list_of_ghi_dfs = []
# make GHI dataset outputs
try:
    list_of_ghi_dfs.append(pd.DataFrame(json_dict[year]["Hourly"]).swapaxes("index", "columns")["GlobHor"])
except TypeError:
    list_of_ghi_dfs.append(pd.DataFrame(data=[(0)], columns=["GHI"]))
except KeyError:
    try:
        list_of_ghi_dfs.append(pd.DataFrame(json_dict[str(year)]["Hourly"]).swapaxes("index", "columns")["GlobHor"])
    except KeyError:
        list_of_ghi_dfs.append(pd.DataFrame(data=[(0)], columns=["GHI"]))
    except TypeError:
        list_of_ghi_dfs.append(pd.DataFrame(data=[(0)], columns=["GHI"]))


hourly_ghi_dfs = pd.concat(list_of_ghi_dfs, axis=1)
hourly_ghi_dfs.to_csv("GHI_Hourly_exports_TMY.csv")

# todo make outputs for the data

pass

