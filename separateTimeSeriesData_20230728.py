import json
import pandas as pd
import os
import Optimization.main as op
import numpy as np

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

# list_of_years = [1996, 1997, 1998]  # todo remove this line when committing, for testing and reducing api calls

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

# load a file if one does not exist
try:
    # check if there is a file to read first
    with open("json_dict_storage.json", "r") as openfile:
        # read the json file
        json_dict = json.load(openfile)
except FileNotFoundError:
    # TODO iterate through all years later

    for i in d_list:
        year = i
        try:
            json_dict[year] = (op.main(d[i], gcr, acdc, year, ac))
        except:
            json_dict[year] = []

json_object = json.dumps(json_dict, indent=4)

# write the json to a file for storage
with open("json_dict_storage.json", "w") as outfile:
    outfile.write(json_object)

# TODO get p50 for each year out
# pd.DataFrame(json_dict[1997]["Hourly"]).swapaxes("index", "columns")["E_Grid"].sum()
#
# # it's already given by this:
# json_dict[1997]["SummaryAnnual"]["netEnergy"]


# Make a list of the p50 values from SRC
list_of_p50s = []


# add those p50's to a dataframe, removing the years that errored from src
for year in list_of_years:
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
df_of_p50s.to_csv("p50s_export.csv")  # export p50s to csv file
dataset_p50 = df_of_p50s.mean()

list_of_hourly_dfs = []

# make 8760 dataset output
for year in list_of_years:
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
hourly_dfs.to_csv("8760_exports.csv")

list_of_ghi_dfs = []
# make GHI dataset outputs
for year in list_of_years:
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
hourly_ghi_dfs.to_csv("GHI_Hourly_exports.csv")

# todo make outputs for the data

pass

