"""Functions for processing and displaying excel exports from Ad Astra."""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def load_schedule_file(filename, courses_only=True):
    """Load Ad Astra schedules file into Dataframe."""
    data = pd.read_excel(filename)
    time_cols = ['Start Time', 'End Time']
    time_pattern = '%I:%M %p'
    date_cols = ['Start Date', 'End Date']
    date_pattern = '%m/%d/%Y'
    
    for col in time_cols:
        data[col] = pd.to_datetime(data[col], format=time_pattern)
        data[col] = data[col] - pd.to_datetime(data[col].dt.date)
    
    for col in date_cols:
        data[col] = pd.to_datetime(data[col], format=date_pattern)

    # calculate lengths of coursetime
    data['Length'] = data['End Time'] - data['Start Time']
    data['Weekly Length'] = data['Length'] * data['Days'].str.len()  # total time per week

    if courses_only:
        data = data[~data['Course/Customer'].str.startswith('Olin College')]
    
    return data


def plot_barh(values, labels, color='blue', fig=None):
    """Plot a horizontal bar chart."""

    if fig is None:
        fig = plt.figure(figsize=(5,20))

    bars = plt.barh(
        tick_label=labels,
        y=np.arange(len(values)),
        height=0.5,
        width=values,
        align='center',
        color=color,
        zorder=3  # bring above gridlines
    )

    # add values to bar chart: https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart#28931750
    rects = bars.patches
    # For each bar: Place a label
    for rect in rects:
        # Get X and Y placement of label from rect.
        x_value = rect.get_width()
        y_value = rect.get_y() + rect.get_height() / 2

        # Number of points between bar and label. Change to your liking.
        space = 5

        # Use X value as label and format number with one decimal place
        label = "{:.1f}".format(x_value)

        # Create annotation
        plt.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(space, 0),          # Horizontally shift label by `space`
            textcoords="offset points", # Interpret `xytext` as offset in points
            va='center',                # Vertically center label
            ha='left')                      # Horizontally align label differently for
                                        # positive and negative values.

    plt.grid(axis='x', linestyle='--', zorder=0)
    fig.patch.set_facecolor('white')
    return fig


def plot_pie(values, labels=None, colors=None, fig=None, **kwargs):
    """Plot a pie chart."""
    if fig is None:
        fig = plt.figure()

    plt.pie(
        values,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        **kwargs
    )
    plt.axis('equal')  # conform to society's beauty standards w/ a circular pie
    fig.patch.set_facecolor('white')


print('reloaded adastra')
