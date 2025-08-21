import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

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
    .agg({
        'precip': 'mean',
        'snow': 'mean',
        'rain': 'mean',
        'precip_day': 'mean',
    })
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
