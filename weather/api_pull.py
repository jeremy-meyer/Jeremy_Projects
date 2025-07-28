import pandas as pd
import numpy as np
import requests
from io import BytesIO
import os
import seaborn as sns
import matplotlib.pyplot as plt

YOURAPIKEY = "<API_KEY>"
base_url_weather_request = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?&aggregateHours=24&"
csv_subdir = 'weather/slc_daily_weather/'


# https://www.visualcrossing.com/resources/documentation/weather-api/weather-api-documentation/

years = range(1980,2025) # Pull from API
location = "Salt Lake City, UT, US"

for year in years:
    start_time = f"{year}-01-01T00:00:00"
    end_time = f"{year}-12-31T00:00:00"
    weather_request = f"{base_url_weather_request}startDateTime={start_time}&endDateTime={end_time}&unitGroup=us&includeAstronomy=true&contentType=csv&location={location}&key={YOURAPIKEY}"
    response = requests.get(weather_request)
    assert response.status_code == 200, "Error: Non-200 code"
    df = pd.read_csv(BytesIO(response.content), header=0)
    df.to_csv(f'{csv_subdir}/slc_{year}.csv', index=False)
    print(f"Finished {year}")

# Write combined file (only need to do once)
filepaths = [csv_subdir+'/'+f for f in os.listdir(csv_subdir) if (f.endswith('.csv') and f.startswith('slc'))]
df_raw = pd.concat(map(lambda x: pd.read_csv(x, index_col=False), filepaths))
combined_df = (
  df_raw
  .sort_values(['Address', 'Date time'])
  .reset_index(drop=True)
)
combined_df['date'] = pd.to_datetime(combined_df['Date time']).dt.date
combined_df.drop(columns=['Date time'], inplace=True)
combined_df.sort_values(by='date', inplace=True)

# Rename columns
combined_df.rename(columns={
    'Minimum Temperature': 'min_temp',
    'Maximum Temperature': 'max_temp',
    'Temperature': 'avg_temp',
    'Wind Chill': 'wind_chill',
    'ASea Level Pressure': 'pressure',
    'Precipitation': 'precipitation',
    'Snow Depth': 'snow_depth',
    'Snowfall': 'snowfall',
    'Wind Speed': 'wind_speed',
}, inplace=True)

combined_df.to_csv(csv_subdir+'/combined_raw.csv', index=False)







# Fit a time of year model to the data. Generate a year avg
# Get other years of data, is there a trend?

# Record highs and lows by month



# When is the 
# Look at snowfall / rainfall extremes
# Plot sunrise/sunset hours

# Longest time without rain

# Atmospheric pressure?

# Todo: Find optimal degrees of freedom
# Is a basic slope term needed?

