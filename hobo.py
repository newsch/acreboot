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
            headers = ['"'+h[0]+'"' for h in headers]  # remove serial number mentions
            outfile.writelines(','.join(headers) + '\n' + infile.read())
    return new_filepath


def process_data(filepath):
    with open(filepath) as file:
        data = pd.read_csv(file,header=0)
    data.index = pd.to_datetime(data['Date Time, GMT-04:00'], format='%m/%d/%y %I:%M:%S %p')
    data.index = data.index.tz_localize(pytz.timezone('GMT')).tz_convert(pytz.timezone('US/Eastern'))  # https://stackoverflow.com/questions/22800079/converting-time-zone-pandas-dataframe
    del data.index.name
    del data['Date Time, GMT-04:00']
    data['dayofweek'] = data.index.dayofweek
    return data


def convert_to_length(data, col):
    view = data[~data[col].isnull()].copy()
    view['delta'] = view.index.to_series().diff()  # calculate differences between times
    return view


def agg_week(data, col):
    view = data[data[col] > 0].groupby('dayofweek')['delta'].agg('sum')
    return view
