import requests
import pandas as pd
from datetime import datetime, timedelta, date

cols_to_rename = {
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
}

# Determine what data needs incremental update
existing_data = pd.read_csv('weather/data_sources/noaa_precip.csv')
start_date = str((pd.to_datetime(max(existing_data[existing_data['precip'].notna()]['date'])) + timedelta(days=1)).date())
end_date = str(date.today() - timedelta(days=1))

# NOAA API configuration
TOKEN = ""
BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
STATION_ID = "USW00024127"  # Salt Lake City Airport station

# Function to fetch data from NOAA API
def fetch_noaa_data(start_date, end_date, station_id, data_types):
    params = {
        "dataset": "daily-summaries",
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": ",".join(data_types),
        "format": "json",
        "units": "standard",
        "includeAttributes": "false",
        "includeStationName": "true",
        "includeStationLocation": "true",
        "token": TOKEN,
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Fetch data
api_data = fetch_noaa_data(start_date, end_date, STATION_ID, cols_to_rename.keys())

# Process data into a DataFrame
if api_data:
    df = pd.DataFrame(api_data)
    df["DATE"] = pd.to_datetime(df["DATE"])
    df.rename(columns=cols_to_rename, inplace=True)
    df.head()
else:
    print("No data retrieved from NOAA API.")



# This code will pull from the noaa source
# It has more accurate precipation data, and the temperature is recorded at the SLC airport

# Ad HOC READ
noaa = pd.read_csv('weather/data-sources/noaa_raw.csv')
noaa.drop(columns=['SN52', 'SN53', 'SX52', 'SX53'], inplace=True)
noaa.rename(columns=cols_to_rename, inplace=True)

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


# Take two
BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
headers = {"token": TOKEN}

params = {
    "datasetid": "GHCND",       # Daily summaries dataset
    "stationid": "GHCND:" + STATION_ID,  # Example: New York Central Park station
    "startdate": start_date,
    "enddate": end_date,
    "datatypeid": "TMAX",       # Daily max temperature
    "limit": 10,
    "units": "standard",
}

# Step 4: Make the request
response = requests.get(BASE_URL, headers=headers, params=params)

# Step 5: Parse response
if response.status_code == 200:
    data = response.json()
    for result in data.get("results", []):
        print(result)
else:
    print("Error:", response.status_code, response.text)
