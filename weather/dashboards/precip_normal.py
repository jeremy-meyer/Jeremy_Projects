import plotly.express as px
import plotly.graph_objects as go
from patsy import dmatrix
from statsmodels import api as sm
from statsmodels.nonparametric.smoothers_lowess import lowess
import pandas as pd
import numpy as np
from patsy import dmatrix
import statsmodels.api as sm

# STEP 1: Clean table and engineer features-----------------------------------

# Subset relevant data
precip_raw = pd.read_csv('weather/data_sources/noaa_precip.csv', index_col=False, parse_dates=['date'])
precip = precip_raw[['date','precip' ,'snow', 'snow_depth', 'tempmin', 'tempmax']].copy()
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
precip['month'] = pd.Categorical(precip['date'].dt.strftime('%b'), categories=month_order, ordered=True)
precip['date'] = pd.to_datetime(precip['date'])
precip['year'] = precip['date'].dt.year
precip['precip_day'] = (precip['precip'] > 0).astype(int)

# Define snow season as Aug - July (I know water season is Oct - Sep, but we have had snow in Sep and I would rather count that in next season)
precip['snow_season'] = np.where(precip['month'].isin(['Aug', 'Sep', 'Oct', 'Nov', 'Dec']), precip['year'], precip['year'] - 1)
precip['snow_season'] = precip['snow_season'].astype(str) + '-' + (precip['snow_season'] + 1).astype(str)

precip['water_year'] = np.where(precip['month'].isin(['Oct', 'Nov', 'Dec']), precip['year']+1, precip['year'] - 1)

def gen_DoY_index(x):
  if x.is_leap_year:
    if x.dayofyear > 60:
      return x.dayofyear - 1
    elif x.dayofyear==60:
      return x.dayofyear - 0.5
  return x.dayofyear

def dayofyear_to_month_day(doy):
  dt = pd.Timestamp(f"2025-01-01") + pd.Timedelta(days=doy-1)
  if doy==59.5:
    return "Feb 29"
  return dt.strftime('%b %d')

precip['day_of_year'] = precip['date'].apply(gen_DoY_index)

# Problem: We don't have a clear way to separate rain from snow. We must make assumptions
# If max_temp < 29, it's all snow
# If min_temp > 37, it's all rain
# Otherwise use 8:1 ratio, since wetter snow is heavier than 10:1
SWE_ratio = 8
precip['rain'] = np.where(
    precip['tempmin'] > 37, precip['precip'], np.where(
        precip['tempmax'] < 29, 0, np.maximum(precip['precip'] - precip['snow']/SWE_ratio, 0)
    )
)
precip['snow_water_equiv'] = precip['precip'] - precip['rain']
# snow_water_equiv + rain = precip

precip.to_csv('weather/output_sources/precip_table.csv', index=False)

# STEP 2: Calculate Normals --------------------------------------
# Calculate daily normals and monthly normals.
N_years = 30
current_year = precip['year'].max()
max_water_year = precip['water_year'].max()
max_winter_year = precip['snow_season'].max()

def offset_season(s, offset):
  return str(int(s.split('-')[0]) + offset) + '-' + str(int(s.split('-')[1]) + offset)

precip = pd.read_csv('weather/output_sources/precip_table.csv', index_col=False, parse_dates=['date'])
precip['month'] = pd.Categorical(precip['date'].dt.strftime('%b'), categories=month_order, ordered=True)
precip_data_for_norm = pd.concat([
  precip[precip['year'].between(current_year - N_years, current_year)]\
    .assign(year_type='calendar_year', current_year=current_year),
  precip[precip['water_year'].between(max_water_year - N_years, max_water_year)]\
    .assign(year_type='water_year', current_year=max_water_year),
  precip[precip['snow_season'].between(offset_season(max_winter_year, - N_years + 1), offset_season(max_winter_year, -1))]\
    .assign(year_type='winter_season', current_year=max_winter_year),
])

monthly_normals = (
    precip_data_for_norm
    .query("year != current_year")
    .query("year_type == 'calendar_year'")
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

monthly_normals.to_csv('weather/output_sources/monthly_precip_normals.csv', index=False)

# Daily Normals Methodology (year / month to date)

calendar_type = 'calendar_year'
metric = 'snow'
ytd = (
  precip_data_for_norm
  .fillna({metric: 0})
  .sort_values(by=['current_year', 'year_type', 'year', 'date'])
  .reset_index(drop=True)
  .groupby(['year_type','year'])
  .apply(lambda x: x.assign(year_to_date_precip=x[metric].cumsum()))
  .reset_index(drop=True)
)

current_year_ytd = ytd.query("year == current_year")
chart_label = current_year_ytd['current_year'].head().iloc[0]

ytd_avg = (
  ytd
  .query("year != current_year")
  .groupby(['year_type','day_of_year'])
  .agg(
      avg_precip_ytd=('year_to_date_precip', 'mean'),
      p10_precip_ytd=('year_to_date_precip', lambda x: np.percentile(x, 10)),
      p25_precip_ytd=('year_to_date_precip', lambda x: np.percentile(x, 25)),
      p50_precip_ytd=('year_to_date_precip', lambda x: np.percentile(x, 50)),
      p75_precip_ytd=('year_to_date_precip', lambda x: np.percentile(x, 75)),
      p90_precip_ytd=('year_to_date_precip', lambda x: np.percentile(x, 90)),
  )
  .reset_index()
  .query("day_of_year != 59.5")
  .query(f"year_type == '{calendar_type}'")
)

ytd_avg.sort_values(by='day_of_year', inplace=True)

fig = px.line(ytd.query("year != current_year"), x='day_of_year', y='year_to_date_precip', color='year', title='Year to Date Precipitation by Year')
fig.update_traces(
    line=dict(color='rgb(0, 100, 0, 0.5)', width=0.75, dash='dot'),
    selector=dict(mode='lines')  # Ensure it applies only to line traces
)
fig.add_scatter(x=current_year_ytd['day_of_year'], y=current_year_ytd['year_to_date_precip'], mode='lines', name=chart_label, line=dict(color='black', width=2))
fig.add_scatter(x=ytd_avg['day_of_year'], y=ytd_avg['avg_precip_ytd'], mode='lines', name='Average', line=dict(color='green', width=4))
fig.add_traces([
    go.Scatter(
        x=list(ytd_avg['day_of_year']) + list(ytd_avg['day_of_year'])[::-1],
        y=list(ytd_avg['p75_precip_ytd']) + list(ytd_avg['p25_precip_ytd'])[::-1],
        fill='toself',
        fillcolor='rgba(0, 150, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='25th-75th Percentile',
    )
])

fig.show(renderer="browser")

ytd_avg['p75_precip_ytd'][ytd_avg['p75_precip_ytd'].isnull()]