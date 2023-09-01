import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from statsmodels.graphics.tsaplots import plot_acf, acf

mood_data_raw = pd.read_csv('github_repos/Jeremy_Projects/mood_tracker/2023_mood_tracker.csv')
weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

mood_data_raw['date'] = pd.to_datetime(mood_data_raw['date'])
mood_data_raw['month'] = pd.to_datetime(mood_data_raw['date'])
mood_data_raw['14_day_avg'] = mood_data_raw['rating'].rolling(window=14, min_periods=3).mean()
mood_data_raw['month_avg'] = mood_data_raw['rating'].rolling(window=28, min_periods=3).mean()
mood_data_unpivoted = pd.melt(mood_data_raw, id_vars=['date'],value_vars=['14_day_avg', 'month_avg'])

# Get histogram of total ratings
ax = sns.histplot(mood_data_raw, x='rating', discrete=True)
ax.set_xticks([x for x in range(-5,6)])
plt.show()

# Show rolling 14 vs rolling month avg
plt.subplots(figsize=(15, 5))
ax = sns.lineplot(mood_data_unpivoted, x='date', y='value',hue='variable')
plt.show()

# Day of week avg
plt.subplots(figsize=(8, 5))
day_avg = mood_data_raw.groupby('day_of_week').aggregate({'rating' : 'mean'}).reindex(weekday_order)
ax = sns.barplot(x=day_avg.index, y='rating', data=day_avg, errorbar=None, color='steelblue')
ax.set(ylabel='rating avg', xlabel='weekday')
plt.show()

# Month avg
plt.subplots(figsize=(8, 5))
month_avg = mood_data_raw.groupby('month').aggregate({'rating' : 'mean'}).reindex(month_order)
month_avg['month'] = [x[:3] for x in month_avg.index.values]
month_avg.set_index('month', inplace=True)
ax = sns.barplot(x=month_avg.index, y='rating', data=day_avg, errorbar=None, color='steelblue')
ax.set(ylabel='rating avg', xlabel='month')
ax.tick_params(axis='x', which='major', labelsize=8)
plt.show()

# Autocorrelation plots
plot_acf(mood_data_raw['rating']) # Pretty much no correlation across time LOL
plt.show()
acf(mood_data_raw['rating'],adjusted=True)

# Manual
mood_data_lagged = mood_data_raw[['rating']].copy()
for i in range(1,20):
  mood_data_lagged[f'lag_{i}'] = mood_data_lagged['rating'].shift(-i)
mood_data_lagged.corr()['rating']

# A day's mood has little reflection from the previous day's mood (correlation near -0.02)
# If positive, we can say that ~2% current rating is reflected in the previous rating
# A negative autocorrelation implies that if a past value is above average the newer value is more likely to be below average 

# "Bad" days
mood_data_lagged[mood_data_lagged['rating']<=0].corr()['rating']


# "Good days"
mood_data_lagged[mood_data_lagged['rating']>=3].corr()['rating']

# Next day is slightly likley to be worse (small correlation)
# Day after is likey to be beter
# No correlation after day 4