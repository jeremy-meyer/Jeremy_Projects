import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from patsy import dmatrix
import statsmodels.api as sm



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
    f"1 + time_index + cc(year_index, df=6, constraints='center', upper_bound=365.25) + month:cc(hourly_index, df=6, constraints='center', upper_bound=24)",
    {"time_index": hourly_model['time_index'], "year_index": hourly_model['year_index'], "hourly_index": hourly_model['hourly_index'], 'month': hourly_model['month']},
    return_type='dataframe'
)


model = sm.OLS(hourly_model['temp'], basis_hourly).fit()
model.summary()
hourly_model['pred_temp'] = model.predict(basis_hourly)

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