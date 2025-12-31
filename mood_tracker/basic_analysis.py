import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date
from statsmodels.graphics.tsaplots import plot_acf, acf

mood_data_raw = pd.read_csv('mood_tracker/2023_mood_data.csv')

weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10] # for weighted moving average
weights_m = list(range(1, 22)) + [21 for x in range(7)] 
keywords = mood_data_raw[~mood_data_raw['keywords'].isnull()]
keywords['keywords'] = keywords["keywords"].copy().apply(lambda x: x.lower().split(", "))

mood_data_raw['date'] = pd.to_datetime(mood_data_raw['date'])
mood_data_raw['year'] = mood_data_raw['date'].apply(lambda x: x.year)
# mood_data_raw['month'] = pd.to_datetime(mood_data_raw['month'])
mood_data_raw['14_day_avg'] = mood_data_raw['rating'].rolling(window=14, min_periods=3).mean()
mood_data_raw['14_day_wavg'] = mood_data_raw['rating'].rolling(window=14).apply(lambda x: (weights*x).sum()/sum(weights), raw=True)
mood_data_raw['month_avg'] = mood_data_raw['rating'].rolling(window=28, min_periods=3).mean()
mood_data_raw['month_wavg'] = mood_data_raw['rating'].rolling(window=28).apply(lambda x: (weights_m*x).sum()/sum(weights_m), raw=True)
mood_data_unpivoted = pd.melt(mood_data_raw, id_vars=['date'],value_vars=['month_wavg', 'month_avg'])

# Get histogram of total ratings
ax = sns.histplot(mood_data_raw, x='rating', discrete=True)
ax.set_xticks([x for x in range(-5,6)])
plt.title('Rating Count')
plt.show()


# Show rolling 14 vs rolling month avg
plt.subplots(figsize=(15, 5))
plt.ylim(bottom=0, top=4)
ax = sns.lineplot(mood_data_unpivoted, x='date', y='value',hue='variable')
plt.legend(title=None)
plt.ylabel('avg rating')
plt.title('Moving Average of Mood Rating')
plt.show()

# Day of week avg
plt.subplots(figsize=(6.75, 4.75))
plt.ylim(bottom=0, top=3.75)
index_ordering = [(x,2023) for x in weekday_order] + [(x,2024) for x in weekday_order] + [(x,2025) for x in weekday_order]
day_avg = mood_data_raw.groupby(["day_of_week", "year"]).aggregate({'rating' : 'mean'}).reindex(index_ordering)
day_avg['year'] = [x[1] for x in day_avg.index]
day_avg['day_of_week'] = [x[0] for x in day_avg.index]
ax = sns.barplot(x="day_of_week", y='rating', data=day_avg, errorbar=None, hue='year', palette='tab10')
ax.set(ylabel='rating avg', xlabel='weekday', title='Weekday Avg')
plt.show()

# Month avg
plt.subplots(figsize=(6.75, 4.75))
plt.ylim(bottom=0, top=3.5)
index_ordering = [(x,2023) for x in month_order] + [(x,2024) for x in month_order] + [(x,2025) for x in month_order]
month_avg = mood_data_raw.groupby(['month', 'year']).aggregate({'rating' : 'mean'}).reindex(index_ordering)
month_avg['month'] = [x[0][:3] for x in month_avg.index]
month_avg['year'] = [x[1] for x in month_avg.index]
ax = sns.barplot(x='month', y='rating', data=month_avg, errorbar=None, hue='year', palette='tab10')
ax.set(ylabel='rating avg', xlabel='month', title='Month Avg')
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

# calendar heatmap
import calplot
import matplotlib.pyplot as plt
cal_input = mood_data_raw['rating'].copy()
cal_input.index = mood_data_raw['date'].copy()
cal_input=cal_input[cal_input.index <= datetime.today()]


fig_mood = calplot.calplot(cal_input,
                suptitle = 'On a scale of -5 to +5, how was your day?',
                suptitle_kws = {'x': 0.5, 'y': 1.0},
                edgecolor = 'black',
                yearlabel_kws = {'fontsize': 20, 'color': 'black'},
                cmap="viridis", # Spectral
                figsize=(16,5.5),
)
plt.show()

# Day of week comparison histogram
recent_data = mood_data_raw.query("date.dt.year == 2025")
day1 = 'Monday'
day2 = 'Friday'

plt.figure(figsize=(7, 6))
sns.histplot(recent_data.query(f"day_of_week=='{day1}'"), x='rating', discrete=True, color='tab:blue', alpha=0.5, label=day1, edgecolor='tab:blue', linewidth=0.75)
sns.histplot(recent_data.query(f"day_of_week=='{day2}'"), x='rating', discrete=True, color='tab:orange', alpha=0.5, label=day2, edgecolor='tab:orange', linewidth=0.75)
plt.xticks([x for x in range(-5,6)])
plt.ylim(bottom=0, top=23)
plt.title(f'{day1} vs {day2} Rating Count (2025)')
plt.legend(title=None)
plt.tight_layout()
plt.show()


# Keywords analysis
keywords_explode = keywords[keywords["date"]>='2024-01-01'].explode("keywords")
keywords_agg = keywords_explode.groupby("keywords").aggregate({'rating' : ['mean', 'count']})
keywords_agg[keywords_agg.rating['count']>=10].sort_values(by=[('rating', 'mean')], ascending=False)
keywords_agg.sort_values(by=[('rating', 'count')], ascending=True)


# Tomorrow:
# Look at common patterns for 5s and 4s
# Look at common patterns for -3s and -2s

# Day of week avg for different parts of the year
plt.subplots(figsize=(8, 5))
plt.ylim(bottom=0, top=3.0)
index_ordering = [(x,'2023H0') for x in weekday_order] + [(x,'2023H1') for x in weekday_order] + [(x,'2024H0') for x in weekday_order]
filtered = mood_data_raw# [mood_data_raw['date']>='2023-07-01'].copy() # mood_data_raw[mood_data_raw['date'].apply(lambda x:x.month) <= 7].copy()
filtered['year_half'] = filtered['year'].apply(str) + 'H' + ((filtered['date'].apply(lambda x:x.month)-1)//6).apply(str)
day_avg = filtered.groupby(["day_of_week", "year_half"]).aggregate({'rating' : 'mean'}).reindex(index_ordering)
day_avg['year_half'] = [x[1] for x in day_avg.index]
day_avg['day_of_week'] = [x[0] for x in day_avg.index]

ax = sns.barplot(x="day_of_week", y='rating', data=day_avg, errorbar=None, hue='year_half')
ax.set(ylabel='rating avg', xlabel='weekday')
plt.show()