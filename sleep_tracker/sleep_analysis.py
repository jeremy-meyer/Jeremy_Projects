import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date
import scipy as sp
import statsmodels.formula.api as smf



# read in data
sleep_raw = pd.read_csv('github_repos/Jeremy_Projects/sleep_tracker/sleep_data.csv')
sleep = sleep_raw[['date', 'rating','asleep', 'woke_up', 'time_asleep_decimal', 'latency' ,'exercise', 'temperature', 'humidity']].copy()
sleep = sleep.rename(columns={'time_asleep_decimal': 'time_asleep'})

def convert_time_to_decimal(time_str, baseline=21, add_24_cutoff=8):
  hour, minute = [int(x) for x in time_str.split(':')]
  if hour <= add_24_cutoff:
    hour += 24
  return (hour*60 + minute)/60 - baseline

# Convert times to decimal (hours)
# Bed time is effecively time I fell asleep
sleep['bed_time'] = sleep['asleep'].apply(convert_time_to_decimal)
sleep['woke_up'] = sleep['woke_up'].apply(convert_time_to_decimal, args=(0, -1))
sleep['latency'] = sleep['latency'].apply(convert_time_to_decimal, args=(0, -1))*60

# Pairs plot
sns.set_theme(style="ticks")
sns.pairplot(sleep)
plt.show()

# Outlier removal
# A temp/humid leverage point will throw off coefficients
# Remove null values from travel dates. It is a confounding variable
sleep = sleep[~sleep['date'].isin(['2024-12-01'])].dropna()

# Simple regression
model = smf.ols(formula='rating ~ exercise + temperature + humidity + bed_time + time_asleep', data=sleep).fit()
print(model.summary())

# Results
#                   coef    std err          t      P>|t|      [0.025      0.975]
# Intercept      -0.8706     10.881     -0.080      0.937     -23.379      21.637
# exercise       -0.2347      0.355     -0.662      0.515      -0.968       0.499
# temperature    -0.0209      0.129     -0.161      0.873      -0.288       0.247
# humidity        0.1564      0.104      1.500      0.147      -0.059       0.372
# bed_time       -1.7951      0.359     -5.003      0.000      -2.537      -1.053
# time_asleep     0.1672      0.273      0.612      0.546      -0.398       0.732

# It looks like bed_time is more important than time asleep! 

# Residuals are kind of normal, but not perfect
plt.hist(model._results.resid, bins=5)
plt.show()

# Center X values
sleep['temperature_c'] = sleep['temperature'] - np.mean(sleep['temperature'])
sleep['humidity_c'] = sleep['humidity'] - np.mean(sleep['humidity'])

model = smf.ols(formula='rating ~ exercise + temperature_c + humidity_c + bed_time + time_asleep', data=sleep).fit()
print(model.summary())
# Intercept is more stable, but other coefficents are similar


# Visual showing bed_time vs sleep_time vs rating
sleep_control = sleep[['date','rating', 'bed_time', 'time_asleep', 'temperature']].copy().dropna()
sleep_control['bed_time_hour'] = np.minimum(np.floor(sleep_control['bed_time'])+21, 23)
sleep_control['hours_asleep'] = np.minimum(np.floor(sleep_control['time_asleep']), 9)
control = sleep_control.groupby(['bed_time_hour', 'hours_asleep'], as_index=False).agg({"rating": [np.mean, len]})

sns.lineplot(data=control[control['hours_asleep']>6], x='hours_asleep', y='rating', hue='bed_time_hour')
#    bed_time_hour  hours_asleep    rating
# 0           22.0           7.0  4.000000
# 1           22.0           8.0  2.833333
# 2           22.0           9.0  4.000000
# 4           23.0           7.0  1.666667
# 5           23.0           8.0  1.800000
# 6           23.0           9.0  2.000000

# Avg rating is higher across the board for bed times before 11pm




# Stepwise regression for feature selection
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from mlxtend.feature_selection import SequentialFeatureSelector

sfs = SequentialFeatureSelector(linear_model.LogisticRegression(),
                                k_features=3,
                                forward=True,
                                scoring='accuracy',
                                cv=None)

columns_to_consider = [x for x in sleep.columns if not (x in ['rating', 'date', 'asleep'])]
X = sleep.drop(columns=['asleep'])[columns_to_consider]
y = sleep['rating']
selected_features = sfs.fit(X, y)
selected_features.k_feature_names_

# Correlate with mood
# Does a good sleep result in a better mood?
mood_data = pd.read_csv('github_repos/Jeremy_Projects/mood_tracker/2023_mood_data.csv')[['date', 'rating']]
mood_data = mood_data[mood_data['date'] >= '2024-11-24']
mood_data = mood_data.rename(columns={'rating': 'mood_rating'})

# Mood is at the end of the day, sleep is at beginning of the day. Can join on dates directly!
mood_sleep = pd.merge(sleep, mood_data, how='left', on=['date'])



# Make 1D scatterplot
def make_1d_scatter(df,xvar, yvar='rating'):
  x_data = df[xvar]
  y_data = df[yvar]
  sns.scatterplot(x=x_data, y=y_data)
  plt.xlabel(xvar)
  plt.ylabel(yvar)

  r, p = sp.stats.pearsonr(x=x_data, y=y_data)
  ax = plt.gca() # G|et a matplotlib's axes instance
  plt.title("R = {:.2f}".format(r))

  # The following code block adds the correlation line:
  m, b = np.polyfit(x_data, y_data, 1)
  X_plot = np.linspace(ax.get_xlim()[0],ax.get_xlim()[1],100)
  plt.plot(X_plot, m*X_plot + b, '-')
  plt.show()

# make_1d_scatter('temperature', 'rating')
make_1d_scatter(mood_sleep, 'rating', 'mood_rating')
# No significant correlation! Bad days in december weren't necessairly related to poor sleep!
# For me, I think this means I am getting good enough sleep that it isn't significantly altering my mood

