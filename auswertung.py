import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from db_helper import DbHelper
from config import *

# get data from db
db_helper = DbHelper(db_user, db_password, db_hostname, db_name)
data = list(reversed(db_helper.get_latest_historic_data(50000)))

times = np.array([item[0] for item in data])
prices = np.array([item[1] for item in data])


# create plot
fig, ax = plt.subplots()

frame = plt.gca()

frame.legend()

# remove labels from x axis
for xlabel_i in frame.axes.get_xticklabels():
    xlabel_i.set_visible(False)
    xlabel_i.set_fontsize(0.0)

# process data
optimised_prices = []
optimised_times = []

for i in range(0, len(times)-1):
    datetime_this = datetime.strptime(times[i], '%d/%m/%Y %H:%M:%S')
    datetime_next = datetime.strptime(times[i+1], '%d/%m/%Y %H:%M:%S')

    # cut out data points where price didn't change
    if prices[i] != prices[i+1]:
        optimised_prices.append(prices[i])
        optimised_times.append(datetime.timestamp(datetime_this) % 86400)
        optimised_prices.append(prices[i+1])
        optimised_times.append(datetime.timestamp(datetime_next) % 86400)


last_day = 0

for i in range(0, len(optimised_times)-1):
    timestamp_this = optimised_times[i]
    timestamp_next = optimised_times[i+1]
    if timestamp_next - timestamp_this < 0:
        ax.plot(optimised_times[last_day:i], optimised_prices[last_day:i])

        last_day = i+2

plt.show()