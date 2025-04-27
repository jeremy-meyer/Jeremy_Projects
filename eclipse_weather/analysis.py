from eclipse_weather.shared_config import *

# Read in data ----------------------------------------------
raw = pd.read_csv(csv_subdir+'/combined_raw.csv', header=0).drop('Unnamed: 0', axis=1)

all_data = (
  raw
  .drop_duplicates(subset=['Address', 'Date time'])
  .rename(columns={'Address': 'city', 'Date time': 'local_time', 'Temperature': 'temperature', 'Cloud Cover': 'cloud_cover'})
)
all_data = all_data[all_data['local_time'].notnull()]

# Read data to fill some missing values (obtained from different source)
def read_one_filled_csv(path, city_name):
  df_read = (
    pd.read_csv(path)
    .rename(columns={'datetime': 'local_time', 'temp': 'temperature', 'cloudcover': 'cloud_cover'})
  )
  df_read['city'] = city_name
  df_read['local_time'] = pd.to_datetime(df_read['local_time']).astype('string')
  return df_read[['city', 'local_time', 'temperature', 'cloud_cover']]

data_for_fill = pd.concat(
  [
    read_one_filled_csv(csv_subdir+'/filled_hourly_values_maz.csv', 'Mazatlan,MX'),
    read_one_filled_csv(csv_subdir+'/filled_hourly_values_torr.csv', 'Torreon,MX')
  ],
  ignore_index=True
).drop_duplicates(subset=['city', 'local_time'])

# Fill missing values - prioritize filled csvs
data_filled = all_data.merge(data_for_fill, on=['city', 'local_time'], how='outer')
data_filled['temperature'] = data_filled['temperature_y'].combine_first(data_filled['temperature_x'])
data_filled['cloud_cover'] = data_filled['cloud_cover_y'].combine_first(data_filled['cloud_cover_x'])
data_filled['local_time'] = pd.to_datetime(data_filled['local_time']) # Convert back to timestamp
# data_filled[data_filled['temperature_y'].isnull() & data_filled['temperature_x'].notnull()] # test
data_filled = data_filled[['city', 'local_time', 'temperature', 'cloud_cover']]

data_filled['year'] = data_filled['local_time'].apply(lambda x: x.year).astype(pd.Int64Dtype())
data_filled['hour'] = data_filled['local_time'].apply(lambda x: x.hour).astype(pd.Int64Dtype())

# Check quality
data_filled.groupby('city').agg({"local_time": "count", "cloud_cover": "count"}) # Mexico cities have so many miss
data_filled[(data_filled['city']=='Torreon,MX')&(data_filled['hour'].between(12,13))].groupby(['year']).agg({"local_time": "count", "cloud_cover": "count"})

# Join on eclipse time
eclipse_times = (
  pd.DataFrame(cities, columns=['batch', 'city','eclipse_time'])
  .drop('batch', axis=1)
)
data_filled = data_filled[data_filled["local_time"] < datetime(2024,1,1)]
data_w_etimes = pd.merge(data_filled, eclipse_times, how='left', on='city')

data_w_etimes['time_to_eclipse'] = (
    data_w_etimes['local_time'] - pd.to_datetime(
    data_w_etimes['local_time'].apply(lambda x: str(x.date())) + 'T' + data_w_etimes['eclipse_time']
  )
) / pd.Timedelta(hours=1)

# cloud cover by year - take +-2hr from totality
cloud_cover_by_year = (
  data_w_etimes[abs(data_w_etimes['time_to_eclipse'])<2]
  .groupby(['city', 'year'])
  .agg({'cloud_cover': 'mean', 'temperature': 'mean'})
  .reset_index()
)
# cloud_cover_by_year[cloud_cover_by_year['city']=='Torreon,MX']

# RESULTS --------------------------------------------------
# overall
(
  cloud_cover_by_year
  .groupby(['city'])
  .agg({'cloud_cover': 'mean', 'temperature': 'mean'})
  .sort_values(['cloud_cover'])
)
# Avg cloud cover for +-2hrs of eclipse
# ciity                 cloud_cover  temperature
# Torreon,MX            34.143841    78.620614
# San Antonio,TX,US     37.546875    75.297917
# Austin,TX,US          38.415625    73.656250
# Jonesboro,AR,US       38.997917    63.452083
# Fort Worth,TX,US      43.535417    69.982292
# Mazatlan,MX           44.896875    78.899306
# Evansville,IN,US      47.844792    62.471875
# Carbondale,IL,US      49.617014    62.402083
# Dallas,TX,US          51.185417    70.287500
# Toledo,OH,US          51.916667    52.991667
# Cleveland,OH,US       54.060417    48.966667
# Erie,PA,US            58.915625    48.826042
# Houlton,ME,US         59.531250    41.245833
# Little Rock,AR,US     61.188542    67.276042
# Fredericton,NB,CA     61.204167    43.677083
# Dayton,OH,US          63.858333    57.088542
# Indianapolis,IN,US    64.160417    57.687500
# Burlington,VT,US      66.522917    47.180208
# Buffalo,NY,US         74.248958    47.800000
# Rochester,NY,US       78.384375    50.238542
# Syracuse,NY,US        78.447917    50.177083
# Gander,NL,CA          82.018478    36.295833

# basic analysis - cloud cover % by hour
data_filled[data_filled['city']=='San Antonio,TX,US'].groupby(['hour']).agg({'cloud_cover': 'mean', 'temperature': 'mean'})
data_filled[data_filled['city']=='Dallas,TX,US'].groupby(['hour']).agg({'cloud_cover': 'mean', 'temperature': 'mean'})

# Compute correlation. Negatives or near 0 are better backup options
by_year = (
  cloud_cover_by_year
  .groupby(['year', 'city'])
  .agg({'cloud_cover': 'mean'})
  .reset_index()
  .pivot(index='year', columns=['city'], values='cloud_cover')
)

by_year.corr()

# What pair of cities have the best odds?
cities_list = by_year.columns.to_list()
all_pairs = list(combinations(cities, 2))
avg_pair = [np.mean(by_year[list(p)].apply(min, axis=1)) for p in all_pairs]
pair_str = [' + '.join(p) for p in all_pairs]
all_pair_cloud_cover = (
  pd.DataFrame(
    [(avg_pair[i], pair_str[i]) for i in range(len(pair_str))], 
    columns=['avg_cloud_cover', 'city_pair']
  )
  .sort_values(['avg_cloud_cover'])
)
# Top 10
all_pair_cloud_cover[:10]
# index      avg_cloud_cover                       city pair
# 3          10.659091        Austin,TX,US + Cleveland,OH,US
# 15         10.711364            Austin,TX,US + Mazatlan,MX
# 7          11.147727       Austin,TX,US + Evansville,IN,US
# 19         11.606818           Austin,TX,US + Toledo,OH,US
# 159        11.836364        Fort Worth,TX,US + Mazatlan,MX
# 152        11.936364         Evansville,IN,US + Torreon,MX
# 77         12.127273         Carbondale,IL,US + Torreon,MX
# 226        12.422727      San Antonio,TX,US + Toledo,OH,US
# 74         12.431818  Carbondale,IL,US + San Antonio,TX,US
# 149        13.463636  Evansville,IN,US + San Antonio,TX,US

# Bottom 10
all_pair_cloud_cover[-10:]

# Let's say you want to go to Dallas as 1st choice
all_pair_cloud_cover[all_pair_cloud_cover['city_pair'].apply(lambda s:"Dallas" in s)]
# Good options are Dallas + San Antonio and Dallas+ OH