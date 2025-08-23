import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Config
N_years = 30
current_year = 2025

# Subset relevant data
precip_raw = pd.read_csv('weather/slc_daily_weather/noaa_slc_airport.csv', index_col=False)
precip = precip_raw[['date','precip' ,'snow', 'snow_depth', 'water_snow_depth', 'tempmin', 'tempmax']].copy()
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
precip['date'] = pd.to_datetime(precip['date'])
precip['year'] = precip['date'].dt.year
precip['month'] = pd.Categorical(precip['date'].dt.strftime('%b'), categories=month_order, ordered=True)
precip['precip_day'] = (precip['precip'] > 0).astype(int)

def gen_DoY_index(x):
  if x.is_leap_year:
    if x.dayofyear > 60:
      return x.dayofyear - 1
    elif x.dayofyear==60:
      return x.dayofyear - 0.5
  return x.dayofyear

precip['day_of_year'] = precip['date'].apply(gen_DoY_index)

# Problem: We don't have a clear way to separate rain and snow
# If max_temp < 29, it's all snow
# If min_temp > 37, it's all rain
# Otherwise use 8:1 ratio, since wetter snow is heavier than 10:1
SWE_ratio = 8
precip['rain'] = np.where(
    precip['tempmin'] > 37, precip['precip'], np.where(
        precip['tempmax'] < 29, 0, np.maximum(precip['precip'] - precip['snow']/SWE_ratio, 0)
    )
)   

precip[precip['snow']>0].sort_values('tempmin', ascending=False).head(10)

precip_normals = (
    precip[precip['year'].between(current_year - N_years, current_year-1)]
    .groupby(['year', 'month'])
    .agg({
        'precip': 'sum',
        'snow': 'sum',
        'rain': 'sum',
        'precip_day': 'mean',
    })
    .reset_index()
    .groupby('month')
    .agg(
        norm_precip=('precip', 'mean'),
        norm_snow=('snow', 'mean'),
        norm_rain=('rain', 'mean'),
        norm_precip_perc=('precip_day', 'mean'),
    )
    .reset_index()
)
print(precip_normals)

# Top 10 snowiest
precip.sort_values('snow', ascending=False).head(10)

# Top 10 rainiest
precip.sort_values('rain', ascending=False).head(10)

# earliest snow
precip[(precip['snow']>0)&(precip['day_of_year']>200)].sort_values('day_of_year', ascending=True).head(10)

# Latest snow
precip[(precip['snow']>0)&(precip['day_of_year']<200)].sort_values('day_of_year', ascending=False).head(10)

last_date = max(precip[precip['precip'].notna()]['date'])

# Compared to normal
precip_anomalies = (
  precip
  .groupby(['year', 'month'])
  .agg(
    precip=('precip', 'sum'),
    snow=('snow', 'sum'),
    rain=('rain', 'sum'),
  )
  .reset_index()
  .merge(precip_normals, on='month', how='left')
  .assign(
    precip_anomaly=lambda x: x['precip'] - x['norm_precip'],
    snow_anomaly=lambda x: x['snow'] - x['norm_snow'],
    rain_anomaly=lambda x: x['rain'] - x['norm_rain'],
    precip_anomaly_perc=lambda x: 100*(x['precip'] / x['norm_precip']-1),
  )
)

precip_anomalies = precip_anomalies[
  (precip_anomalies['year'] < current_year) | (precip_anomalies['month'] < last_date.strftime('%b'))
]
precip_anomalies['date'] = pd.to_datetime(precip_anomalies['year'].astype(str) + '-' + precip_anomalies['month'].astype(str) + '-01')
precip_anomalies['time_index'] = (precip_anomalies['date'].dt.month - 1) + (precip_anomalies['date'].dt.year - precip_anomalies['year'].min()) * 12


precip_year = (
  precip_anomalies
  .groupby(['year'])
  .agg(
    precip=('precip', 'mean'),
    count=('precip', 'count'),
  )
  .reset_index()
)

precip_year = precip_year[precip_year['count']==12]
precip_year = precip_year.drop(['count'], axis=1)
precip_year['month'] = 'Year'
precip_w_year = pd.concat([precip_anomalies, precip_year])
precip_w_year['month'] = pd.Categorical(precip_w_year['month'], categories=month_order+["Year"], ordered=True)


precip_w_year['rank'] = (
    precip_w_year.groupby('month')['precip']
    .rank(method='min', ascending=True)
)

monthly_pivot_rank = precip_w_year.pivot(index='month', columns='year', values='rank')

dry_to_moist_colors = ['#865513','#D2B469', '#F4E8C4', '#F5F5F5', '#CBE9E5', '#69B3AC', '#20645E']
dry_to_moist_cmap = LinearSegmentedColormap.from_list("dry_to_moist", dry_to_moist_colors)

# Rainfall rank
plt.figure(figsize=(17, 6.5))
sns.heatmap(
    monthly_pivot_rank,
    cmap=dry_to_moist_cmap,
    vmax=max(precip_w_year['rank']),
    vmin=1,
    center=(max(precip_w_year['rank'])+1)/2,
    annot=True,
    fmt=".0f",
    linewidths=0.005,
    cbar_kws={'label': 'Rank'},
    annot_kws={"size": 8}
)
plt.title('Monthly Precipitation Rank')
plt.xlabel('Year')
plt.ylabel('Month')
plt.tight_layout()
plt.show()

# Total Precip
monthly_pivot_total = precip_w_year.pivot(index='month', columns='year', values='precip')
plt.figure(figsize=(17, 6.5))
sns.heatmap(
    monthly_pivot_total,
    cmap=dry_to_moist_cmap,
    annot=True,
    center=1.5,
    vmax=3,
    vmin=0.0,
    fmt=".1f",
    linewidths=0.005,
    cbar_kws={'label': 'Total Precipitation (inches)'},
    annot_kws={"size": 7}
)
plt.title('Monthly Precipitation')
plt.xlabel('Year')
plt.ylabel('Month')
plt.tight_layout()
plt.show()

# Departure from normal 
monthly_pivot_anom = precip_anomalies.pivot(index='month', columns='year', values='precip_anomaly_perc')
plt.figure(figsize=(17, 6.5))
sns.heatmap(
    monthly_pivot_anom,
    cmap=dry_to_moist_cmap,
    annot=True,
    center=0,
    vmax=100,
    vmin=-100,
    fmt=".0f",
    linewidths=0.005,
    cbar_kws={'label': 'Total Precipitation (inches)'},
    annot_kws={"size": 7}
)
plt.title('Monthly Precipitation % departure from normal')
plt.xlabel('Year')
plt.ylabel('Month')
plt.tight_layout()
plt.show()

# Is there a long term trend of precipation?
from patsy import dmatrix
import statsmodels.api as sm

model_precip = precip_anomalies[precip_anomalies['year'].between(current_year - N_years, current_year-1)].copy()

basis = dmatrix(
    f"1 + month + time_index",
    {"time_index": model_precip['time_index'], "month": model_precip['month']},
    return_type='dataframe'
)

# Predict fitted values
model = sm.OLS(model_precip['precip'], basis).fit()
model.summary()
model_precip['predictions'] = round(model.predict(basis),2)

sns.lineplot(data=model_precip, x='date', y='predictions')
sns.lineplot(data=model_precip, x='date', y='precip', alpha=0.5, color='gray')
plt.title('Long Term Precipitation Trend')
plt.xlabel('Year')
plt.ylabel('Precipitation (inches)')
plt.tight_layout()
plt.show()

# What about year total?
# Not quite enough to suggest significance. Maybe slight
precip_year_model = precip_year.copy()
precip_year_model['year_index'] = precip_year_model['year'] - precip_year_model['year'].min()

basis_year = dmatrix(
    f"1 + year",
    {"year": precip_year_model['year_index']},
    return_type='dataframe'
)

model_year = sm.OLS(precip_year_model['precip'], basis_year).fit()
model_year.summary()
precip_year_model['predictions'] = round(model_year.predict(basis_year),2)
sns.lineplot(data=precip_year_model, x='year', y='predictions')
sns.lineplot(data=precip_year_model, x='year', y='precip', alpha=0.5, color='gray')
plt.title('Long Term Precipitation Trend')
plt.xlabel('Year')
plt.ylabel('Precipitation (inches)')
plt.tight_layout()
plt.show()

# Todo: Longest streak of drought
# Create a column to track whether precipitation is 0
precip['is_dry'] = (precip['precip'] == 0).astype(int)

# Calculate the longest streak of consecutive 0 precipitation
precip['dry_streak'] = precip['is_dry'] * (
    precip['is_dry'].groupby((precip['is_dry'] != precip['is_dry'].shift()).cumsum()).cumcount() + 1
)

precip['dry_streak_group'] = precip['dry_streak'].groupby()

precip.sort_values(by='dry_streak', ascending=False).head(20) # 46 days in 2005!!!


(precip['is_dry'] != precip['is_dry'].shift()).head(10)
precip['is_dry'].head(10)

# Snowfall
snow = (
  precip
  .groupby(['year'])
  .agg(
    snow=('snow', 'sum'),
  )
  .reset_index()
  .query("year < @current_year")
  .assign(
    year_index=lambda x: x['year'] - x['year'].min()
  )
)

snow.sort_values(by='snow', ascending=False).head(10)
basis_snow = dmatrix(
    # f"1 + cr(year_index, df=2, constraints='center')",
    f"1 + year_index",
    {"year_index": snow['year_index']},
    return_type='dataframe'
)

model_snow = sm.OLS(snow['snow'], basis_snow).fit()
model_snow.summary() # Significance, snow is decreasing! Around -0.6in/year
snow['forecast'] = model_snow.predict(basis_snow)

sns.lineplot(data=snow, x='year', y='snow', color='gray', alpha=0.5)
sns.lineplot(data=snow, x='year', y='forecast', color='blue')
plt.title('Annual Snowfall')
plt.xlabel('Year')
plt.ylabel('Snowfall (inches)')
plt.ylim(0, None)
plt.show()