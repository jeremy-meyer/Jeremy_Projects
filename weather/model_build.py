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

# Create cyclic cubic spline basis for day_of_year (period=365)
spline_basis = dmatrix(
    "1 + total_years + cc(day_of_year, df=10)",  # Find optimal df
    {"day_of_year": model_df['day_of_year'], "total_years": model_df['total_years']},
    return_type='dataframe'
)

# Fit linear regression to the spline basis
model = LinearRegression(fit_intercept=False)
model.fit(spline_basis, temperatures['max_temp'])

# statsmodels
model_sm = sm.OLS(temperatures['max_temp'], spline_basis).fit()
model_sm.summary()

# Predict fitted values
model_df['yhat'] = model.predict(spline_basis)
model_df['year_effect'] =   model_sm.params['total_years'] * model_df['total_years']
model_df['error'] = model_df['max_temp'] - model_df['yhat']
plt.hist(model_df['error'], bins=51, edgecolor='black')
plt.show()

# Plot actual and fitted values for recent years
plt.figure(figsize=(12, 6))
mask = model_df['date'] >= '2000-01-01'
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'max_temp'], label='Actual', color='blue', alpha=0.5)
plt.plot(model_df.loc[mask, 'date'], model_df.loc[mask, 'yhat'], label='Spline Fit', color='red', linewidth=2)
plt.xlabel('Date')
plt.ylabel('Max Temperature (°F)')
plt.title('Max Temperature with Cyclic Cubic Spline Seasonality')
plt.legend()
plt.tight_layout()
plt.show()