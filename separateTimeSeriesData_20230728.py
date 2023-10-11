import json
import pandas as pd
import os
import Optimization.main as op
import Optimization.functions.read_data as read_data
import numpy as np

cwd = os.getcwd()
filename = "SG-90074-2309-19-1_TShourly.csv"  # for SolarAnywhere this will be the time series folder
# filename = "ElevenMile_TimeSeries_ACP__20230728_adjusted.csv"
project_dir = "ElevenMile"
data_source = "SolarGIS"  # "Vaisala", "SolarAnywhere" or "SolarGIS"
filepath = os.path.join(cwd, "Data", project_dir, filename)

# TODO Make seperate import functions for each dataset (time series)
df = read_data.read_dataset(data_source, filepath, "ts")

# get list of unique years from dataframe
list_of_years = list(df.index.year.unique())

# list_of_years = [1996, 1997, 1998]  # todo remove this line when committing, for testing and reducing api calls

# make dict of years with df for each year
d = {}

# for year in list_of_years:
#     d[year] = df.loc[f"{year}-1-1 1:00":f"{year+1}-1-1 0:00"] # need to adjust this to make the year extend to the next january 1st at midnight

if data_source == "SolarGIS":
    for year in list_of_years:
        d[year] = df.loc[f"{year}-1-1 0:30":f"{year}-12-31 23:30"]

else:
    for year in list_of_years:
        d[year] = df.loc[
                f"{year}-1-1 1:00":f"{year + 1}-1-1 0:00"]  # need to adjust this to make the year extend to the next january 1st at midnight

# TODO implement optimization
json_list = []
json_dict = {}


# Manually enter GCR and AC/DC ratio and ACCapacity
gcr = 35  # percentage
acdc = 1.3  # eg: 1.3
ac = 100000
d_list = d.keys()

# load a file if one does not exist TODO uncomment for later
# try:
#     # check if there is a file to read first
#     with open(f"Data/{project_dir}/json_dict_storage.json", "r") as openfile:
#         # read the json file
#         json_dict = json.load(openfile)
# except FileNotFoundError:
#     # TODO iterate through all years later

for i in d_list:
    year = i
    try:
        if len(d[i]) > 8760:
            d[i] = d[i].iloc[:-24]
        json_dict[year], src_response_code = (op.main(d[i], gcr, acdc, year, ac))
    except:
        print()
        json_dict[year] = []

json_object = json.dumps(json_dict, indent=4)

# write the json to a file for storage TODO turning this off to account for extra data sources
# with open(f"Data/{project_dir}/json_dict_storage.json", "w") as outfile:
#     outfile.write(json_object)

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
df_of_p50s.to_csv(f"Data/{project_dir}/p50s_export_{data_source}.csv")  # export p50s to csv file
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
hourly_dfs.to_csv(f"Data/{project_dir}/8760_exports_{data_source}.csv")

list_of_ghi_dfs = []
# make GHI dataset outputs
for year in list_of_years:
    try:
        list_of_ghi_dfs.append(pd.DataFrame(json_dict[year]["Hourly"]).swapaxes("index", "columns")["GlobHor"])
    except TypeError:
        list_of_ghi_dfs.append(pd.DataFrame(data=[(0)], columns=["GHI"]))
    except KeyError:
        try:
            list_of_ghi_dfs.append(pd.DataFrame(json_dict[str(year)]["Hourly"]).swapaxes("index", "columns")["GlobalHor"])
        except KeyError:
            list_of_ghi_dfs.append(pd.DataFrame(data=[(0)], columns=["GHI"]))
        except TypeError:
            list_of_ghi_dfs.append(pd.DataFrame(data=[(0)], columns=["GHI"]))


hourly_dfs = pd.concat(list_of_ghi_dfs, axis=1)
hourly_dfs.to_csv(f"Data/{project_dir}/GHI_Hourly_exports_{data_source}.csv")

# todo make outputs for the data

pass

