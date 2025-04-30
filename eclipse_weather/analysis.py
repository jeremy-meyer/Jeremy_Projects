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
data_filled[(data_filled['city']=='Mazatlan,MX')&(data_filled['hour'].between(11,12))].groupby(['year']).agg({"local_time": "count", "cloud_cover": "count"})

# Join on eclipse time
eclipse_times = (
  pd.DataFrame(cities, columns=['batch', 'city','eclipse_time'])
  .drop('batch', axis=1)
)

data_w_etimes = pd.merge(data_filled, eclipse_times, how='left', on='city')

data_w_etimes['time_to_eclipse'] = (
    data_w_etimes['local_time'] - pd.to_datetime(
    data_w_etimes['local_time'].apply(lambda x: str(x.date())) + 'T' + data_w_etimes['eclipse_time']
  )
) / pd.Timedelta(hours=1)


# cloud cover by year - take +-1hr from totality
cloud_cover_by_year = (
  data_w_etimes[abs(data_w_etimes['time_to_eclipse'])<2]
  .groupby(['city', 'year'])
  .agg({'cloud_cover': 'mean', 'temperature': 'mean'})
  .reset_index()
)

cloud_cover_by_year[cloud_cover_by_year['cloud_cover'].isnull()]
# If yearly value is null, overwrite with daily avg

daily_avg = (
  data_w_etimes.groupby(['city', 'year'])
  .agg({'cloud_cover': 'mean', 'temperature': 'mean'}).reset_index()
  .merge(manual_fill_by_year, on=['city', 'year'], how='left', suffixes=['', '_new'])
)

# Fill in additional values found from online
daily_avg['cloud_cover'] = daily_avg['cloud_cover_new'].combine_first(daily_avg['cloud_cover'])
daily_avg['temperature'] = daily_avg['temperature_new'].combine_first(daily_avg['temperature'])
daily_avg = daily_avg.drop(['cloud_cover_new', 'temperature_new'], axis=1)

cloud_by_year = (
  cloud_cover_by_year
  .merge(daily_avg, on=['city', 'year'], how='outer', suffixes=['', '_day_avg'])
)

# Fill in additional values found from online
cloud_by_year['cloud_cover'] = cloud_by_year['cloud_cover'].combine_first(cloud_by_year['cloud_cover_day_avg'])
cloud_by_year['temperature'] = cloud_by_year['temperature'].combine_first(cloud_by_year['temperature_day_avg'])
cloud_by_year = cloud_by_year.drop(['cloud_cover_day_avg', 'temperature_day_avg'], axis=1).reset_index()

cloud_by_year[cloud_by_year['cloud_cover'].isnull()] # Check

# RESULTS --------------------------------------------------
# overall
truth = (
  cloud_by_year[cloud_by_year['year']==2024][['city', 'cloud_cover']]
  .rename({'cloud_cover': '2024_cloud_%'}, axis=1)
)

cloud_by_year_train = (
  cloud_by_year[cloud_by_year['year'] < 2024] # Assume we don't know 2024
)


(
  cloud_by_year_train
  .groupby(['city'])
  .agg({'cloud_cover': 'mean', 'temperature': 'mean'})
  .sort_values(['cloud_cover'])
  .reset_index()
  .merge(truth, on=['city'], how='left')
)
#                   city  cloud_cover  temperature  2024_cloud_%
# 0           Torreon,MX    34.320977    77.027253        90.000
# 1    San Antonio,TX,US    37.040833    75.660000        98.150
# 2         Austin,TX,US    37.625833    74.080000        96.525
# 3     Fort Worth,TX,US    42.128333    70.635833        39.200
# 4          Mazatlan,MX    42.779444    78.730833        60.000
# 5      Jonesboro,AR,US    45.584167    63.510000         0.000
# 6     Carbondale,IL,US    48.081944    63.166667         0.000
# 7     Evansville,IN,US    48.973333    63.087222         9.725
# 8         Dallas,TX,US    49.423333    70.676667        61.750
# 9      Cleveland,OH,US    55.594167    48.225000         0.800
# 10        Toledo,OH,US    57.255000    52.387500         0.000
# 11       Houlton,ME,US    59.039167    41.271667         0.000
# 12          Erie,PA,US    59.660278    48.026944        55.400
# 13   Little Rock,AR,US    60.308333    67.607500        48.800
# 14   Fredericton,NB,CA    60.630000    43.665000        12.925
# 15    Burlington,VT,US    65.777222    46.415833        85.300
# 16        Dayton,OH,US    66.991667    57.973333        37.800
# 17  Indianapolis,IN,US    67.123333    58.048333        48.200
# 18       Buffalo,NY,US    75.116667    47.114167        87.450
# 19      Syracuse,NY,US    76.315000    49.105833        95.675
# 20     Rochester,NY,US    77.294167    49.265833       100.000
# 21        Gander,NL,CA    80.880833    36.128333        94.000

# basic analysis - cloud cover % by hour
data_w_etimes[data_w_etimes['city']=='San Antonio,TX,US'].groupby(['hour']).agg({'cloud_cover': 'mean', 'temperature': 'mean'})
data_w_etimes[data_w_etimes['city']=='Dallas,TX,US'].groupby(['hour']).agg({'cloud_cover': 'mean', 'temperature': 'mean'})

# Compute correlation. Negatives or near 0 are better backup options
cities_ordered = [x[1] for x in cities]
cloud_year_pivot = (
  cloud_by_year_train
  .pivot(index='year', columns=['city'], values='cloud_cover')
  [cities_ordered] # Order cities
)

# make a correlation chart
plt.figure(figsize=(16, 10))
sns.heatmap(cloud_year_pivot.corr(), cmap='viridis', annot=True, fmt='.2f', vmax=1)
plt.title("2024 Eclipse Cloud Cover Correlation matrix", fontsize=20)
plt.savefig('cloud_cover_correlation.png', bbox_inches='tight')
plt.show()

# What pair of cities have the best odds?
all_pairs = list(combinations(cities_ordered, 2))
avg_pair = [np.mean(cloud_year_pivot[list(p)].apply(min, axis=1)) for p in all_pairs]
truth_pair = [np.min(truth[truth['city'].isin(p)]['2024_cloud_%']) for p in all_pairs]

pair_str = [' + '.join(p) for p in all_pairs]
all_pair_cloud_cover = (
  pd.DataFrame(
    [(pair_str[i], avg_pair[i], truth_pair[i]) for i in range(len(pair_str))], 
    columns=['city_pair', 'avg_cloud_cover', '2024_cloud_%']
  )
  .sort_values(['avg_cloud_cover'])
)

# Join on true result
# Top 10
all_pair_cloud_cover[:10]
#                                city_pair  avg_cloud_cover  2024_cloud_%
# 28        Torreon,MX + Evansville,IN,US        14.680556         9.725
# 23        Torreon,MX + Fort Worth,TX,US        14.816944        39.200
# 22            Torreon,MX + Austin,TX,US        15.909444        90.000
# 27        Torreon,MX + Carbondale,IL,US        16.348889         0.000
# 2            Mazatlan,MX + Austin,TX,US        16.375833        60.000
# 31            Torreon,MX + Toledo,OH,US        16.697500         0.000
# 21       Torreon,MX + San Antonio,TX,US        16.704722        90.000
# 45  San Antonio,TX,US + Jonesboro,AR,US        18.084167         0.000
# 65      Austin,TX,US + Evansville,IN,US        18.520000         9.725
# 24            Torreon,MX + Dallas,TX,US        18.723889        61.750

# Ususual cloud cover in Mexico and S Texas in 2024!

# Top 10 (US only)
all_pair_cloud_cover[all_pair_cloud_cover['city_pair'].apply(lambda x: not ',MX' in x)][:10]
#                                 city_pair  avg_cloud_cover  2024_cloud_%
# 206   Jonesboro,AR,US + San Antonio,TX,US        18.084167         0.000
# 7         Austin,TX,US + Evansville,IN,US        18.520000         9.725
# 2         Austin,TX,US + Carbondale,IL,US        19.134444         0.000
# 13         Austin,TX,US + Jonesboro,AR,US        19.811667         0.000
# 74   Carbondale,IL,US + San Antonio,TX,US        20.253333         0.000
# 19            Austin,TX,US + Toledo,OH,US        20.693333         0.000
# 157    Fort Worth,TX,US + Jonesboro,AR,US        21.238333         0.000
# 3          Austin,TX,US + Cleveland,OH,US        21.240000         0.800
# 226      San Antonio,TX,US + Toledo,OH,US        21.529167         0.000
# 149  Evansville,IN,US + San Antonio,TX,US        21.603333         9.725

# All of these would have been great choices for 2024!


# Bottom 10 (worst on avg - most are geographically close!)
all_pair_cloud_cover[-10:]

# Let's say you want to go to Dallas as 1st choice
all_pair_cloud_cover[all_pair_cloud_cover['city_pair'].apply(lambda s:"Dallas" in s)]
# Good options are Dallas + Jonesboro, AR  and Dallas+ OH

# 2D matrix visual -------------------------------------
result_matrix = pd.DataFrame([
  [np.mean(cloud_year_pivot[list({c, c2})].apply(min, axis=1)) for c in cities_ordered] for c2 in cities_ordered], 
  columns=cities_ordered,
  index=cities_ordered,
)

plt.figure(figsize=(16, 10))
colors = ['#4283DA','#8cc0fe','#D0DFEF','#979797','#6D6D6D']
sky_cloud_cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
sns.heatmap(result_matrix, cmap=sky_cloud_cmap, annot=True, fmt='.0f', vmax=100.0, vmin=0.0)
plt.title("Pairwise Cloud Cover %", fontsize=20)
plt.savefig('cloud_cover_2d_matrix.png', bbox_inches='tight')
plt.show()

# hourly cloud cover map
hour_cloud_avg = (
  data_w_etimes
  .groupby(['city', 'hour'])
  .agg({'cloud_cover': 'mean'})
  .reset_index()
)

cities_for_chart = ['Austin,TX,US','Dallas,TX,US','Evansville,IN,US','Cleaveland,OH,US','Houlton,ME,US']
input_for_chart = hour_cloud_avg[hour_cloud_avg['city'].isin(cities_for_chart)].copy()
input_for_chart['cloud_cover'] = input_for_chart['cloud_cover'].astype('float')
input_for_chart['hour'] = input_for_chart['hour'].astype('int')

sns.lineplot(data=input_for_chart, x='hour', y='cloud_cover', hue='city')
plt.ylim(20,80)
plt.title("Average Cloud Cover by Hour", fontsize=12)
plt.savefig('avg_cloud_cover_hour.png', bbox_inches='tight')
plt.show()