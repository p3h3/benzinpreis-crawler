import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from db_helper import DbHelper
from config import *
import pickle

offline = False

color_lookup = [
    "red",
    "orange",
    "yellow",
    "greenyellow",
    "green",
    "cyan",
    "blue"
]


def find_nearest_index(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx


def save_load(opt, obj=""):
    if opt == "save":
        # Saving the objects:
        with open('data_e10.pkl', 'wb') as f:
            pickle.dump(obj, f)
            print('data saved')
    elif opt == "load":
        with open('data_e10.pkl', "rb") as f:
            return pickle.load(f)
    else:
        print('Invalid saveLoad option')


# calculating percentage differences between two arrays and outputting them as a new array
def calculate_percentage_difference(values, average):
    differences = []
    for i in range(len(values)):
        try:
            differences.append((100 * (values[i] - average)) / values[i])
        except IndexError:
            differences.append(0)
    return differences


if __name__ == "__main__":
    if not offline:
        # get data from db
        db_helper = DbHelper(db_user, db_password, db_hostname, db_name)
        data = list(reversed(db_helper.get_latest_historic_data(5000)))
        save_load("save", data)
    else:
        data = save_load("load")
        print("first:", data[0][0])

    times = np.array([item[0] for item in data])
    prices = np.array([item[1] for item in data])

    # create plot
    fig, ax = plt.subplots()

    frame = plt.gca()

    frame.legend()

    # process data
    optimised_prices = []
    optimised_times = []

    time_unit_size_s = 86400

    for i in range(0, len(times) - 1):
        datetime_this = datetime.strptime(times[i], '%d/%m/%Y %H:%M:%S')
        datetime_next = datetime.strptime(times[i + 1], '%d/%m/%Y %H:%M:%S')

        #if datetime_this.hour != datetime_next.hour:
        #    print(datetime.timestamp(datetime_this) % time_unit_size_s, " = ", datetime_this.strftime("%A %H:%M"))

        # cut out data points where price didn't change
        if prices[i] != prices[i + 1]:  # and 15 < datetime_this.hour < 24:
            optimised_prices.append(prices[i])
            optimised_times.append(datetime.timestamp(datetime_this))
            optimised_prices.append(prices[i + 1])
            optimised_times.append(datetime.timestamp(datetime_next))

    last_time_unit = 0

    for i in range(0, len(optimised_times) - 1):
        timestamp_this = optimised_times[i] % time_unit_size_s
        timestamp_next = optimised_times[i + 1] % time_unit_size_s
        if timestamp_next - timestamp_this < 0:
            weekday = datetime.fromtimestamp(optimised_times[i+1]).weekday()
            time_unit_times = np.array(optimised_times[last_time_unit:i]) % time_unit_size_s
            time_unit_prices = np.array(optimised_prices[last_time_unit:i]) % time_unit_size_s

            weekstart = int(optimised_times[i])
            while datetime.fromtimestamp(weekstart).weekday() != 0:
                weekstart -= 300

            weekprices = optimised_prices[find_nearest_index(optimised_times, weekstart)
                                          :
                                          find_nearest_index(optimised_times, weekstart + (86400 * 7))]
            average = float(sum(time_unit_prices) / len(time_unit_prices))

            time_unit_percentages = calculate_percentage_difference(time_unit_prices, average)

            start = find_nearest_index(time_unit_times, 63000)
            end = find_nearest_index(time_unit_times, 66000)

            # every day has a different color
            #if weekday == 3:
            ax.plot(time_unit_times, time_unit_percentages, color=color_lookup[weekday])

            last_time_unit = i + 1

    # plt.xticks([0,100000,200000,300000], "moin")

    plt.show()


# ergebnis: am tag immer zwischen 17:45 und 19:15 diesel tanken gehen
# ergebnis: am tag immer zwischen 18:00 und 19:00 oder 22:00 und 00:00 e10 tanken gehen
