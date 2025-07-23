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

years = range(2000,2023) # Pull from API
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

# read in combined file
full_data = pd.read_csv(csv_subdir+'/combined_raw.csv', index_col=False)

temperatures = full_data[['date', 'min_temp', 'max_temp']].copy()
temperatures['date'] = pd.to_datetime(temperatures['date'])
temperatures['year'] = temperatures['date'].dt.year
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
temperatures['month'] = pd.Categorical(temperatures['date'].dt.strftime('%b'), categories=month_order, ordered=True)

# Coldest days
temperatures.sort_values(by='min_temp')[['date', 'min_temp']].head(10)

# Warmest days
temperatures.sort_values(by='max_temp', ascending=False)[['date', 'max_temp']].head(10)

# Greatest minimum
temperatures.sort_values(by='min_temp', ascending=False)[['date', 'min_temp']].head(10)

# Coldest Maximum
temperatures.sort_values(by='max_temp')[['date', 'max_temp']].head(10)

# Warmest and coldest by year
yearly_extremes = (
    temperatures
    .groupby('year')
    .agg({'max_temp': 'max', 'min_temp': 'min'})
    .reset_index()
)

# Find the date for each year's max and min temperature
yearly_extremes['date_max_temp'] = yearly_extremes.apply(
    lambda row: temperatures[(temperatures['year'] == row['year']) & (temperatures['max_temp'] == row['max_temp'])]['date'].iloc[0],
    axis=1
)
yearly_extremes['date_min_temp'] = yearly_extremes.apply(
    lambda row: temperatures[(temperatures['year'] == row['year']) & (temperatures['min_temp'] == row['min_temp'])]['date'].iloc[0],
    axis=1
)
yearly_extremes

# Warmest/coldest by month
monthly_extremes = (
    temperatures
    .groupby('month')
    .agg({'max_temp': 'max', 'min_temp': 'min'})
    .reset_index()
    .sort_values(by='month')
)

# Greatest/Least temperature range in a single day
temp_swing = (
    temperatures
    .assign(temp_swing=lambda x: x['max_temp'] - x['min_temp'])
    .sort_values(by='temp_swing', ascending=False)
    .drop(columns=['year', 'month', 'avg_temp'])
)
temp_swing.head(10)
temp_swing.sort_values(by='temp_swing', ascending=True).head(10)

# Number of 100+ degree days by year
(
    temperatures
    .assign(above_100=lambda x: x['max_temp'] > 100)
    .groupby('year')
    .agg({'above_100': 'sum'})
    .reset_index()
    .sort_values(by='year')
)

# Number of days below 10 in a year
(
    temperatures
    .assign(below_10=lambda x: x['min_temp'] < 10)
    .groupby('year')
    .agg({'below_10': 'sum'})
    .reset_index()
    .sort_values(by='year')
)



# Create a seaborn lineplot
plt.figure(figsize=(12, 6))
sns.lineplot(data=temperatures[temperatures['date']>='2020-01-01'], x='date', y='max_temp', color='blue')

# Add labels and title
plt.xlabel('Date')
plt.ylabel('Temperature (°F)')
plt.title('Daily Temperature Over Time')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# Show the plot
plt.tight_layout()
plt.show()

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

