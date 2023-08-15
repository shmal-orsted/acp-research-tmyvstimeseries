import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_data(json_dict):
    """
    plotting data from the api calls
    :param json_dict: dictionary with the values that came from the api call
    :return:
    """

    # make arrays of data
    # plot is ncf y axis, dc/ac x axis
    # ncf list
    #TODO make lists for each GCR
    # TODO lists should have the points of each DC/AC ratio and NCF associated with them
    # TODO get the points you need for each GCR list
    # TODO plot the lines individually on the plot

    # check the json_dict for each unique GCR value
    #GCR list
    gcr_list = []

    for scen in json_dict:
        if json_dict[scen]["SystemAttributes"]["GCR"] in gcr_list:
            pass
        else:
            gcr_list.append(json_dict[scen]["SystemAttributes"]["GCR"])

    # make lists for each gcr found
    # make dict of gcr's in the gcr_list for list points
    points_dict = {}

    for i in gcr_list:
        points_dict[i] = []

    for scen in json_dict:

        ncf = json_dict[scen]["NCF"]
        dcac = json_dict[scen]["SystemAttributes"]["DCCapacity"]/json_dict[scen]["SystemAttributes"]["ACCapacity"]

        # add those to the dict for points
        points_dict[json_dict[scen]["SystemAttributes"]["GCR"]].append((ncf, dcac))

    # plot each list
    for r in gcr_list:
        y,x = zip(*points_dict[r])
        plt.plot(x,y, label=f"GCR: {r}")

    # plot options
    plt.ylabel("NCF")
    plt.xlabel("DC/AC Ratio")

    #plot legend
    plt.legend(loc="right")

    # save and show image
    plt.savefig("exports/fig.png")
    plt.show()
    return