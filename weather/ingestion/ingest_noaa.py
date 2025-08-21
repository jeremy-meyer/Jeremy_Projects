import pandas as pd

# This code will pull from the noaa source
# It has more accurate precipation data, and the temperature is recorded at the SLC airport

noaa = pd.read_csv('weather/slc_daily_weather/noaa_raw.csv')
noaa.drop(columns=['SN52', 'SN53', 'SX52', 'SX53'], inplace=True)
noaa.rename(columns={
    'DATE': 'date',
    'TMAX': 'tempmax',
    'TMIN': 'tempmin',
    'TAVG': 'tempavg',
    'PRCP': 'precip',
    'SNOW': 'snow',
    'SNWD': 'snow_depth',
    'STATION': 'station',
    'NAME': "location",
    'ACMH': 'avg_cloud',
    'ACSH': 'avg_cloud_daytime',
    'AWND': 'avg_wind',
    'PSUN': 'sun_perc',
    'SN02': 'min_soil_temp_10cm',
    'SN03': 'min_soil_temp_20cm',
    'SX02': 'max_soil_temp_10cm',
    'SX03': 'max_soil_temp_20cm',
    'TSUN': 'sunshine_hours',
    'WDF2': 'wind_direction',
    'WESD': 'water_snow_depth',
}, inplace=True)

# noaa.to_csv("weather/slc_daily_weather/noaa_slc_airport.csv", index=False)

# Quality Test
# (
#   noaa[['date', 'precip', 'snow' ,'tempmax', 'tempmin']]
#   [noaa['year']>=2023]
#   .sort_values(by='snow', ascending=False)
# ).head(10)

# (
#   noaa[noaa['year']==1972]
#   .groupby('month')
#   .agg({
#       'tempmax': 'max',
#       'tempmin': 'min',
#       'tempavg': 'mean',
#       'precip': 'sum',
#       'snow': 'sum',
#       'snow_depth': 'max'
#   })
# )

# nan_percent = noaa.isna().mean() * 100
# print(nan_percent)

## Todo: Pull from API