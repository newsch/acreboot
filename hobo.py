import csv
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import pytz


def strip_header_serial(fp):
    filename, ext = os.path.splitext(fp)
    new_filepath = filename+'_fixed'+ext
    HEADER_PATTERN = re.compile(r'"([^"()]+)( \([\w \d/:,]+\))?"')
    with open(fp) as infile:
        with open(new_filepath, 'w') as outfile:
            infile.readline()  # skip first line
            headers = HEADER_PATTERN.findall(infile.readline())
            headers = ['"'+h[0]+'"' for h in headers]  # remove serial number mentionsastimezone
            outfile.writelines(','.join(headers) + '\n' + infile.read())
    return new_filepath


def process_data(filepath):
    with open(filepath) as file:
        data = pd.read_csv(file,header=0)
    eastern = pytz.timezone('US/Eastern')
    data.index = pd.to_datetime(data['Date Time, GMT-04:00'], format='%m/%d/%y %I:%M:%S %p')
    data.index = (data.index + pd.to_timedelta(4, 'h')).tz_localize(pytz.timezone('GMT')).tz_convert(eastern)  # https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
    del data.index.name
    del data['Date Time, GMT-04:00']
    data['dayofweek'] = data.index.dayofweek
    data['date'] = data.index.normalize()
    return data


def convert_to_length(data, col):
    view = data[~data[col].isnull()].copy()
    view['delta'] = view.index.to_series().diff()  # calculate differences between times
    return view


def agg_week(data, col):
    view = data[data[col] == 0].groupby('dayofweek')['delta'].agg('sum')
    return view

def plot_by_day(data, col):
    start = data[:1].index.date[0]
    end = data[-1:].index.date[0]

    day_totals = get_weekday_count(start, end)
    data_by_day = agg_week(convert_to_length(data, col), col)
    print(sum(data_by_day / day_totals / np.timedelta64(1, 'h')))
    print(sum((data_by_day / day_totals / np.timedelta64(1, 'h'))[0:5]))
    fig = plt.figure()
    plt.bar(
        data_by_day.index,
        data_by_day / day_totals / np.timedelta64(1, 'h'),
    )
    plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    plt.xlabel('Day of Week')
    fig.patch.set_facecolor('white')  # needed for dark theme https://stackoverflow.com/questions/14088687/how-to-change-plot-background-color
    return fig


def get_weekday_count(start, end):
    days = pd.DataFrame(pd.date_range(start=start, end=end, freq='D', tz='US/Eastern'), columns=['date'])
    days['dayofweek'] = days['date'].dt.dayofweek
    day_totals = days.groupby('dayofweek')['date'].agg('count')  # total number of each day of the week
    return day_totals
