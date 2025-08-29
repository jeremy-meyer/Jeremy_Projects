import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from patsy import dmatrix
import statsmodels.api as sm

hourly_raw = pd.read_csv('weather/slc_daily_weather/slc_hourly_weather.csv')
hourly_raw['timestamp'] = pd.to_datetime(hourly_raw['timestamp'])
hourly_raw['year'] = pd.to_datetime(hourly_raw['timestamp']).dt.year
hourly_raw['month'] = pd.to_datetime(hourly_raw['timestamp']).dt.strftime('%b')
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
hourly_raw['month'] = pd.Categorical(hourly_raw['month'], categories=month_order, ordered=True)


hourly_model = hourly_raw[['timestamp', 'temp', 'day', 'year', 'month']].copy()
hourly_model['time_index'] = (
  (hourly_model['timestamp'] - hourly_model['timestamp'].min()).dt.total_seconds() / (60*60*24)
)
hourly_model['year_index'] = (
  hourly_model['time_index'] % 365.25
)
hourly_model['hourly_index'] = (
  hourly_model['timestamp'].dt.hour
)


basis_hourly = dmatrix(
    f"1 + time_index + cc(year_index, df=6, constraints='center', upper_bound=365.25) + month:cc(hourly_index, df=9, constraints='center', upper_bound=24)",
    {"time_index": hourly_model['time_index'], "year_index": hourly_model['year_index'], "hourly_index": hourly_model['hourly_index'], 'month': hourly_model['month']},
    return_type='dataframe'
)

# basis_hourly2 = dmatrix(
#     f"1 + time_index + cc(year_index, df=6, constraints='center', upper_bound=365.25) + month:C(hourly_index)",
#     {"time_index": hourly_model['time_index'], "year_index": hourly_model['year_index'], "hourly_index": hourly_model['hourly_index'], 'month': hourly_model['month']},
#     return_type='dataframe'
# )


model = sm.OLS(hourly_model['temp'], basis_hourly).fit()
model.summary()
hourly_model['pred_temp'] = model.predict(basis_hourly)

# model2 = sm.OLS(hourly_model['temp'], basis_hourly2).fit()
# model2.summary()
# hourly_model['pred_temp'] = model.predict(basis_hourly)

data = hourly_model[hourly_model['day'].between('2025-07-01', '2025-08-15')]
sns.lineplot(
  data=data,
  x='timestamp',
  y='temp',
)
sns.lineplot(
  data=data,
  x='timestamp',
  y='pred_temp',
)

plt.xticks(rotation=45)
plt.show()

# Compare time of day seasonality for each month
# Additive decomposition
# Multiply each term in the design matrix by its coefficient
coefficients = model.params
hourly_model['time_trend'] = basis_hourly['time_index'] * coefficients['time_index']
hourly_model['year_seasonality'] = (
    basis_hourly.filter(like='cc(year_index').dot(coefficients.filter(like='cc(year_index'))
)

hourly_model['hourly_seasonality'] = (
    basis_hourly.filter(like='(hourly_index').dot(coefficients.filter(like='(hourly_index'))
)

hourly_model['intercept'] = coefficients['Intercept']

# Calculate the total predicted temperature as the sum of all components
hourly_model['pred_temp_decomposed'] = (
    hourly_model['intercept'] +
    hourly_model['time_trend'] +
    hourly_model['year_seasonality'] +
    hourly_model['hourly_seasonality']
)

# Verify that the decomposed prediction matches the model's prediction
assert np.allclose(hourly_model['pred_temp'], hourly_model['pred_temp_decomposed'])

# Compare hourly effects across month
hourly_effects = hourly_model.groupby(['month', 'hourly_index']).agg(
    hourly_seasonality=('hourly_seasonality', 'mean')
).reset_index()

hottest_hours = hourly_effects.loc[hourly_effects.groupby('month')['hourly_seasonality'].idxmax()]
coldest_hours = hourly_effects.loc[hourly_effects.groupby('month')['hourly_seasonality'].idxmin()]

# Plot the hourly_effects for each month as separate lines
plt.figure(figsize=(12, 6))
sns.lineplot(data=hourly_effects, x='hourly_index', y='hourly_seasonality', hue='month')
sns.scatterplot(
    data=hottest_hours,
    x='hourly_index',
    y='hourly_seasonality',
    color='red',
    legend=False,
    s=25,  # Size of the dots
    marker='o'
)
sns.scatterplot(
    data=coldest_hours,
    x='hourly_index',
    y='hourly_seasonality',
    color='blue',
    legend=False,
    s=25,  # Size of the dots
    marker='o'
)
plt.title('Hourly avg temperature anomalies by Month')
plt.xlabel('Hour of Day')
plt.ylabel('Temperature (F)')
plt.xticks(range(24))
plt.legend(title='Month', bbox_to_anchor=(1.115, 1), loc='upper right')
plt.show()

# Super interesting! Winter months have a less pronounced hourly seasonality effect compared to summer months
# Coldest time of day is around 6am in Summertime, warmest is around 4pm
# In Winter, the coldest time can be as late as 9am (-1hr for DST), warmest can be around 3pm (+1hr for DST) in fall / early winter
hottest_hours
coldest_hours
# Why does the .fit() produce a large condition number?

hourly_model[hourly_model['day']=='2024-03-10']

