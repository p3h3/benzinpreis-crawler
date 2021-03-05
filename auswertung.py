import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from db_helper import DbHelper
from config import *
import pickle

offline = True


def save_load(opt, obj=""):
    if opt == "save":
        # Saving the objects:
        with open('data.pkl', 'wb') as f:
            pickle.dump(obj, f)
            print('data saved')
    elif opt == "load":
        with open('data.pkl', "rb") as f:
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
        data = list(reversed(db_helper.get_latest_historic_data(1000000)))
        save_load("save", data)
    else:
        data = save_load("load")

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

        if datetime_this.hour != datetime_next.hour:
            print(datetime.timestamp(datetime_this) % time_unit_size_s, " = ", datetime_this.strftime("%A %H:%M"))

        # cut out data points where price didn't change
        if prices[i] != prices[i + 1]:  # and 15 < datetime_this.hour < 24:
            optimised_prices.append(prices[i])
            optimised_times.append(datetime.timestamp(datetime_this) % time_unit_size_s)
            optimised_prices.append(prices[i + 1])
            optimised_times.append(datetime.timestamp(datetime_next) % time_unit_size_s)

    last_time_unit = 0

    for i in range(0, len(optimised_times) - 1):
        timestamp_this = optimised_times[i]
        timestamp_next = optimised_times[i + 1]
        if timestamp_next - timestamp_this < 0:
            time_unit_times = optimised_times[last_time_unit:i]
            time_unit_prices = optimised_prices[last_time_unit:i]

            average = float(sum(time_unit_prices) / len(time_unit_prices))

            time_unit_percentages = calculate_percentage_difference(time_unit_prices, average)

            ax.plot(time_unit_times, time_unit_percentages)

            last_time_unit = i + 1

    # plt.xticks([0,100000,200000,300000], "moin")

    plt.show()


# ergebnis: am tag immer zwischen 17:45 und 19:15 diesel tanken gehen
# ergebnis: am tag immer zwischen 18:00 und 19:00 oder 22:00 und 00:00 e10 tanken gehen
