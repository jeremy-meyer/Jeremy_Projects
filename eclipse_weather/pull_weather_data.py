from eclipse_weather.shared_config import *

# https://www.visualcrossing.com/resources/documentation/weather-api/weather-api-documentation/

years = range(1994,2000) # Pull from API

for year in years:
  all_dfs = []
  for b, t in batch_times.items():
    cities_to_pull = [c[1] for c in cities if c[0]==b]
    start_time = f"{year}-04-08T{t[0]}:00:00"
    end_time = f"{year}-04-08T{t[1]}:00:00"
    locations = '|'.join(cities_to_pull)

    weather_request = f"{base_url_weather_request}startDateTime={start_time}&endDateTime={end_time}&unitGroup=us&contentType=csv&location={locations}&key={YOURAPIKEY}"
    response = requests.get(weather_request)
    assert response.status_code == 200, "Error: Non-200 code"
    all_dfs.append(pd.read_csv(BytesIO(response.content), header=0))
    print(f"Finished year {year}, batch {b}")

  combined_df = reduce(lambda x,y: pd.concat([x,y]), all_dfs)
  combined_df.to_csv(f'{csv_subdir}/weather_{year}.csv', index=False)

# Write combined file (only need to do once)
filepaths = [csv_subdir+'/'+f for f in os.listdir(csv_subdir) if (f.endswith('.csv') and f.startswith('weather'))]
df_raw = pd.concat(map(lambda x: pd.read_csv(x, index_col=False), filepaths))
combined_df = (
  df_raw[['Address', 'Date time','Temperature', 'Cloud Cover']]
  .sort_values(['Address', 'Date time'])
)
combined_df['Date time'] = pd.to_datetime(combined_df['Date time']).astype('string') # string for merge

combined_df.to_csv(csv_subdir+'/combined_raw.csv')


# QA
# pd.read_csv(csv_subdir+'/combined.csv').groupby('Address').agg({"Date time": "count", "Cloud Cover": "count"})
# start_time = f"2019-04-08T00:00:00"
# end_time = f"2019-04-08T23:00:00"
# locations = 'Torreón, COAH, México'

# weather_request_test = f"{base_url_weather_request}startDateTime={start_time}&endDateTime={end_time}&unitGroup=us&contentType=csv&location={locations}&key={YOURAPIKEY}"
# response = requests.get(weather_request_test)
# pd.read_csv(BytesIO(response.content))[['Address','Date time', 'Cloud Cover']]
# pd.DataFrame(response.json()['locations']['Mazatlan,MX']['values'])