import streamlit as st

from google.cloud import storage
from dateutil.parser import parse
import datetime
import pandas as pd
import numpy as np
import pytz
import matplotlib.pyplot as plt

@st.cache(persist=True)
def load_data():
    storage_client = storage.Client('dotufp')
    blobs = list(storage_client.list_blobs('dotufp-raw'))

    return [{'name': blob.name, 'time_created': blob.time_created, 'size': blob.size} for blob in blobs]

def dotufp_dashboard_chart_function(df, column_to_chart):
    """Initial/Temp plotting function."""
    fig, ax = plt.subplots(figsize=(15,7))

    list_of_collectors = ['twitter_faves', 'twitter_home_timeline', 'twitter_timeline', 'web_scrape']

    for collector in list_of_collectors:

        twitter_faves_df = df[df['collector'] == collector]
        twitter_faves_df['cumulative_size_bytes'] = twitter_faves_df['size_bytes'].cumsum()
        ax.plot(twitter_faves_df['timestamp'], twitter_faves_df[column_to_chart], label=collector)

    ax.legend()
    ax.set_title(column_to_chart)

    # x = st.info("Loading...")
    # with st.echo():
    #     x.pyplot(fig)
    st.pyplot(fig)

st.write("vaqmr dashboard")

n = 7 # n-day report

blobs = load_data()

raw_files = []
for blob in blobs:
    if blob['name'].find('comics') >= 0:
        continue

    collector, storage_key, blob_name = blob['name'].split('/')
    timestamp = parse(blob_name.split('.')[0]) # blob.time_created is tz aware

    today = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    n_days_ago = today - datetime.timedelta(days=n)

    if blob['time_created'] > n_days_ago:
        raw_files.append({'collector': collector,
                          'storage_key': storage_key,
                          'timestamp': timestamp,
                          'size_bytes': blob['size']})


raw_files_df = pd.DataFrame(raw_files)
raw_files_df.sort_values(by=['timestamp'], inplace=True)
# raw_files_df['cumulative_size_bytes'] = raw_files_df['size_bytes'].cumsum()

raw_files_pivot = raw_files_df.pivot_table(index=['collector', 'storage_key'],
                                            values=['storage_key', 'size_bytes'],
                                            aggfunc={'storage_key': len,
                                                    'size_bytes': [np.mean, sum]})

st.table(raw_files_pivot)

dotufp_dashboard_chart_function(raw_files_df, 'size_bytes')
dotufp_dashboard_chart_function(raw_files_df, 'cumulative_size_bytes')