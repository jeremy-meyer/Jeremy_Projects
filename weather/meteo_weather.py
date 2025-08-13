
# Combine data
import pandas as pd

csvs = [
    pd.read_csv(f'weather/slc_daily_weather/{decade}.csv')
    for decade in range(1970, 2021, 10)
]

pd.read_csv(f'weather/slc_daily_weather/combined_slc_weather.csv').columns

raw_data = pd.concat(csvs)

refined_data = (
    raw_data
    .rename(columns={
		'time': 'date',
        'precipitation_sum (inch)': 'precip',
        'precipitation_hours (h)': 'precip_hours',
        'snowfall_sum (inch)': 'snow',
		'snow_depth_max (inch)': 'snow_depth',
        'rain_sum (inch)': 'rain',
        'temperature_2m_mean (°F)': 'mean_temp',
        'temperature_2m_max (°F)': 'max_temp',
        'temperature_2m_min (°F)': 'min_temp',
        'apparent_temperature_max (°F)': 'feels_like_max',
		'apparent_temperature_min (°F)': 'feels_like_min',
        'apparent_temperature_mean (°F)': 'feels_like_mean',
		'wind_speed_10m_max (mp/h)': 'wind_speed_max',
        'wind_direction_10m_dominant (°)': 'wind_direction',
        'wind_speed_10m_mean (mp/h)': 'wind_speed_mean',
        'sunrise (iso8601)': 'sunrise',
		'sunset (iso8601)': 'sunset',
        'weather_code (wmo code)': 'weather_code',
        'dew_point_2m_mean (°F)': 'dew_point',
        'snowfall_water_equivalent_sum (inch)': 'snow_water_equivalent',
        'pressure_msl_mean (hPa)': 'pressure_mean',
        'visibility_mean (undefined)': 'visibility_mean',
        'cloudcover_mean (%)': 'cloud_cover',
        'soil_temperature_0_to_7cm_mean (°F)': 'soil_temp',
        'relative_humidity_2m_mean (%)': 'humidity',
        'cloud_cover_mean (%)': 'cloud_cover',
	})
)
refined_data['year'] = pd.to_datetime(refined_data['date']).dt.year

refined_data.groupby('year').agg({
	'precip': 'sum',
    'snow': 'sum',
    'rain': 'sum',
    'max_temp': 'max',
	'min_temp': 'min',
}).sort_values(by='year').reset_index()

refined_data[refined_data['year']==2023][['date', 'max_temp', 'min_temp']].head(60)