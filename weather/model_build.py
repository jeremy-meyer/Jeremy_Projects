from patsy import dmatrix
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import pandas as pd
from matplotlib import pyplot as plt
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
model_df['yhat'] = model.predict(basis_1)
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

# plot error over time for both models
plt.plot(model_df['date'], model_df['error_mv_avg'], label='Model 1 Error', color='orange', alpha=0.7)
plt.plot(model_df['date'], model_df['error_mv_avg2'], label='Model 2 Error', color='green', alpha=0.7)
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
plt.xlabel('Date')
plt.ylabel('Max Temperature (°F)')
plt.title('Max Temperature with Cyclic Cubic Spline Seasonality')
plt.legend()
plt.tight_layout()
plt.show()


# Plot all components
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




# Todo later: yearly seasonality term changes over time
# Adding a trend term