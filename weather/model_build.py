from patsy import dmatrix
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date
import seaborn as sns


csv_subdir = 'weather/slc_daily_weather/'
full_data = pd.read_csv(csv_subdir+'/combined_raw.csv', index_col=False)

temperatures = full_data[['date', 'avg_temp', 'min_temp', 'max_temp']].copy()
temperatures['date'] = pd.to_datetime(temperatures['date'])
temperatures['year'] = temperatures['date'].dt.year
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
temperatures['month'] = pd.Categorical(temperatures['date'].dt.strftime('%b'), categories=month_order, ordered=True)


# Prepare day-of-year feature
model_df = temperatures.copy()
model_df['day_of_year'] = (
    model_df['date'].dt.dayofyear / model_df['date'].dt.is_leap_year.apply(lambda x: 366 if x else 365)
)

model_df['total_years'] = ((model_df['date'] - model_df['date'].min()).dt.days) / 365.25


METRIC = 'avg_temp'
# Model 1: Fit a cyclic cubic spline without taking into account groth across years
# Center the time of year effect so we can interpret the other coefficients separately
basis_1 = dmatrix(
    "1 + cc(day_of_year, df=12, constraints='center')",  # Find optimal df
    {"day_of_year": model_df['day_of_year'], "total_years": model_df['total_years']},
    return_type='dataframe'
)

# statsmodels
model_sm = sm.OLS(temperatures[METRIC], basis_1).fit()
model_sm.summary()

# Predict fitted values
model_df['yhat'] = model_sm.predict(basis_1)
model_df['year_effect'] =   model_sm.params['total_years'] * model_df['total_years']
model_df['error'] = model_df[METRIC] - model_df['yhat']
model_df['error_mv_avg'] = model_df['error'].rolling(window=365, min_periods=180).mean()
plt.hist(model_df['error'], bins=51, edgecolor='black')
plt.show()


# model 2: Fit a cyclic cubic spline with a trend term
basis_2 = dmatrix(
    "1 + total_years + cc(day_of_year, df=12, constraints='center')",
    {"day_of_year": model_df['day_of_year'], "total_years": model_df['total_years']},
    return_type='dataframe'
)

model_sm2 = sm.OLS(temperatures[METRIC], basis_2).fit()
model_sm2.summary()

# Predict fitted values
model_df['yhat2'] = model2.predict(basis_2)
model_df['year_effect'] =   model_sm2.params['Intercept'] + model_sm2.params['total_years'] * model_df['total_years']
model_df['error2'] = model_df[METRIC] - model_df['yhat2']
model_df['error_mv_avg2'] = model_df['error2'].rolling(window=365, min_periods=180).mean()

# model 3: Fit a cyclic cubic spline with a trend term. More complicated trend term
basis_3 = dmatrix(
    "1 + cr(total_years, df=3, constraints='center') + cc(day_of_year, df=12, constraints='center')",
    {"day_of_year": model_df['day_of_year'], "total_years": model_df['total_years']},
    return_type='dataframe'
)

model_sm3 = sm.OLS(temperatures[METRIC], basis_3).fit()
model_sm3.summary()

# Predict fitted values
model_df['yhat3'] = model_sm3.predict(basis_3)
model_df['error3'] = model_df[METRIC] - model_df['yhat3']
model_df['error_mv_avg3'] = model_df['error3'].rolling(window=365, min_periods=180).mean()

# plot error over time for both models
plt.plot(model_df['date'], model_df['error_mv_avg'], label='Model 1 Error', color='orange', alpha=0.7)
plt.plot(model_df['date'], model_df['error_mv_avg2'], label='Model 2 Error', color='green', alpha=0.7)
plt.plot(model_df['date'], model_df['error_mv_avg3'], label='Model 3 Error', color='red', alpha=0.7)
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.title('Model Error Over Time')
plt.xlabel('Date')
plt.ylabel('Error (°F)')
plt.legend()
plt.show()


# Plot actual and fitted values for recent years
plt.figure(figsize=(12, 6))
mask = model_df['year'] == 2024
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, METRIC], label='Actual', color='blue', alpha=0.5)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'yhat'], label='Model 1', color='red', linewidth=1)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'yhat2'], label='Model 2', color='orange', linewidth=1)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'yhat3'], label='Model 3', color='green', linewidth=1)
plt.xlabel('Date')
plt.ylabel('Max Temperature (°F)')
plt.title('Max Temperature with Cyclic Cubic Spline Seasonality')
plt.legend()
plt.tight_layout()
plt.show()


# Plot all components (2)
plt.figure(figsize=(12, 6))
mask = model_df['year'] >= 2010
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, METRIC], label='Actual', color='blue', alpha=0.5)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'year_effect'], label='Trend', color='orange', linewidth=1)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'yhat2'], label='Trend + Year', color='red', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Max Temperature (°F)')
plt.title('Additive decomposition for {metric}')
plt.legend()
plt.tight_layout()
plt.show()

coefs3 = model_sm3.params
trend_params = coefs3[[x for x in coefs3.index if ('total_years' in x) or (x=='Intercept')]]
DoY_params = coefs3[[x for x in coefs3.index if 'day_of_year' in x]]

# Todo later: yearly seasonality term changes over time
# Adding a trend term

# Multiply trend_params with corresponding columns in basis_3
model_df['trend_effect'] = basis_3[trend_params.index].values @ trend_params.values
model_df['trend_plus_DoY'] = model_df['trend_effect'] + basis_3[DoY_params.index].values @ DoY_params.values


plt.figure(figsize=(12, 6))
mask = model_df['year'] >= 1980
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, METRIC], label='Actual', color='blue', alpha=0.5)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'trend_effect'], label='Trend', color='orange', linewidth=1)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'trend_plus_DoY'], label='Trend + Year', color='red', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Max Temperature (°F)')
plt.title(f'Additive decomposition for {METRIC}')
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
mask = model_df['year'] >= 1980
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, METRIC], label='Actual', color='blue', alpha=0.5)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'trend_effect'], label='Trend', color='orange', linewidth=1)
# plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'trend_plus_DoY'], label='Trend + Year', color='red', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Max Temperature (°F)')
plt.title(f'Additive decomposition for {METRIC}')
plt.legend()
plt.tight_layout()
plt.show()

(
  model_df
  .groupby('year')
  .agg({'trend_effect': 'mean'})
  .reset_index()
)

# "Normals"
N_years = 30
current_year = date.today().year

# Create 1/2 index for leap year so we can intepret "hottest day of year" correctly
def gen_DoY_index(x):
  if x.is_leap_year:
    if x.dayofyear > 60:
      return x.dayofyear - 1
    elif x.dayofyear==60:
      return x.dayofyear - 0.5
  return x.dayofyear


data_for_normal = temperatures.loc[model_df['year'].between(current_year - N_years, current_year-1)].copy()
data_for_normal['day_of_year'] = data_for_normal['date'].apply(gen_DoY_index)
data_for_normal['date_formatted'] = data_for_normal['date'].dt.strftime('%b-%d')

# Set upper bound to 366 so Jan 1 and Dec 31 have different predicted values
basis_normal = dmatrix(
    "1 + cc(day_of_year, df=8, constraints='center', upper_bound=366)",
    {"day_of_year": data_for_normal['day_of_year'],},
    return_type='dataframe'
)

# Predict fitted values
model_norm = sm.OLS(data_for_normal['max_temp'], basis_normal).fit()
model_norm.summary()
data_for_normal['normal'] = round(model_norm.predict(basis_normal),2)

sns.scatterplot(data_for_normal, x='day_of_year', y='max_temp', legend=None, alpha=0.4, color='red', size=3)
sns.lineplot(data_for_normal[data_for_normal['year']==2024], x='day_of_year', y='normal', color='darkred', linewidth=2)
plt.title('Average High Temperatures')
plt.show()

# Avg hottest/coldest day of the year?
(
  data_for_normal[data_for_normal['year']==2024]
  [['day_of_year','date_formatted','normal']]
  .sort_values(by='normal', ascending=False)
)
# July 25th/26th is the hottest day of the year
# Jan 5th is coldest day of the year

(
  data_for_normal
  .groupby('date_formatted')
  .agg({'max_temp': 'mean'})
  .reset_index()
  .sort_values(by='max_temp', ascending=False)
  .head(10)
)

data_for_normal[data_for_normal['year']==2024] # check endpints

# 10/90 Bands
percentiles = (
    data_for_normal
    .groupby('day_of_year')['max_temp']
    .agg(p10=lambda x: x.quantile(0.1), p90=lambda x: x.quantile(0.9))
    .reset_index()
)

# Create basis for 10/90 bands
basis_9010 = dmatrix(
    "1 + cc(day_of_year, df=8, constraints='center', upper_bound=366)",
    {"day_of_year": percentiles['day_of_year'],},
    return_type='dataframe'
)

model_percentiles_10 = sm.OLS(percentiles['p10'], basis_9010).fit()
percentiles['lower_10'] = round(model_percentiles_10.predict(basis_9010),2)

model_percentiles_90 = sm.OLS(percentiles['p90'], basis_9010).fit()
percentiles['upper_90'] = round(model_percentiles_90.predict(basis_9010),2)


# Fit a spline to this
sns.scatterplot(percentiles, x='day_of_year', y='p10', label='10th Percentile', color='blue', alpha=0.5)
sns.lineplot(percentiles, x='day_of_year', y='lower_10', color='darkblue', linewidth=2)
sns.scatterplot(percentiles, x='day_of_year', y='p90', label='90th Percentile', color='red', alpha=0.5)
sns.lineplot(percentiles, x='day_of_year', y='upper_90', color='darkred', linewidth=2)
plt.show()

data_for_normal['lower_10'] = model_percentiles_10.predict(basis_normal)
data_for_normal['upper_90'] = model_percentiles_90.predict(basis_normal)

# Put everything together
sns.scatterplot(data_for_normal, x='day_of_year', y='max_temp', legend=None, alpha=0.3, color='black', size=2)
sns.lineplot(data_for_normal[data_for_normal['year']==2024], x='day_of_year', y='normal', color='red', linewidth=2)
sns.lineplot(data_for_normal[data_for_normal['year']==2024], x='day_of_year', y='lower_10', color='red', linewidth=1, ls='--')
sns.lineplot(data_for_normal[data_for_normal['year']==2024], x='day_of_year', y='upper_90', color='red', linewidth=1, ls='--')
plt.title('Average High Temperatures')
plt.show()






# Todo: Find optimal knots for cyclic cubic spline