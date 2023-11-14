import io, base64
from io import BytesIO
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64
from matplotlib.ticker import LinearLocator
import numpy as np
from datetime import timedelta, date, timezone, datetime
from homeinsightprj.settings import TIME_ZONE
from .models import *
import datetime, time
import pytz

def utc_to_local(utc_dt):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_dt + offset

def month_converter(index):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months[index]

def get_dataset_ndays(usage, n_days):
    last_date = usage[len(usage)-1].timestamp
    first_date = last_date-timedelta(days=n_days)
    dataset_last_n_days = usage.filter(timestamp__range=(first_date, last_date))
    return dataset_last_n_days

def make_timepoints(last_n_days):
    last_n_days_timeList=[]
    for point in last_n_days:
        last_n_days_timeList.append(str(utc_to_local(point.timestamp)))
    return last_n_days_timeList
    
def get_mean(last_m_days, resample):
    timelist=[]
    q = last_m_days.values('timestamp', 'value')
    dataset = pd.DataFrame.from_records(q)
    mean = dataset.resample(resample, on='timestamp').mean()
    values = list(mean["value"])
    value= ["{0:0.3f}".format(i) for i in values]
    time = pd.to_datetime(mean.index.values)
    for point in time:
        timelist.append(str(point))
    return  timelist, value

#use to plot to image with matplotlib
# def get_plot(days,counts):
#     fig, ax = plt.subplots(figsize=(10,4))
#     ax.plot(days, counts, '--bo')

#     fig.autofmt_xdate()
#     ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
#     ax.set_title('By date')
#     ax.set_ylabel("Count")
#     ax.set_xlabel("Date")
#     ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
#     ax.yaxis.set_minor_locator(LinearLocator(25))

#     flike = io.BytesIO()
#     fig.savefig(flike)
#     b64 = base64.b64encode(flike.getvalue()).decode()
#     return b64