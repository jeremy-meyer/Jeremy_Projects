import pandas as pd
import numpy as np
import requests
import os
from functools import reduce
from itertools import combinations
from datetime import date, datetime
from io import StringIO, BytesIO
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


YOURAPIKEY = ''
base_url_weather_request = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?&aggregateHours=1&"
csv_subdir = 'eclipse_weather/weather_data'


cities = [
  (1, 'Mazatlan,MX', '11:09:33'),
  (1, 'Torreon,MX', '12:19:01'),

  (2, 'San Antonio,TX,US', '13:34:19'),
  (2, 'Austin,TX,US', '13:37:01'),
  (2, 'Fort Worth,TX,US', '13:41:43'),
  (2, 'Dallas,TX,US', '13:42:38'),
  (2, 'Little Rock,AR,US', '13:52:50'),

  (3, 'Jonesboro,AR,US', '13:56:49'),
  (3, 'Carbondale,IL,US', '14:01:20'),
  (3, 'Evansville,IN,US', '14:04:09'),

  (4, 'Indianapolis,IN,US', '15:07:58'),
  (4, 'Dayton,OH,US', '15:10:50'),
  (4, 'Toledo,OH,US', '15:13:16'),
  (4, 'Cleveland,OH,US', '15:15:40'),
  (4, 'Erie,PA,US', '15:18:14'),

  (5, 'Buffalo,NY,US', '15:20:13'),
  (5, 'Rochester,NY,US', '15:21:58'),
  (5, 'Syracuse,NY,US', '15:23:46'),
  # (5, 'Montreal,CA,US', '15:27:33'),
  (5, 'Burlington,VT,US', '15:27:45'),
  (5, 'Houlton,ME,US', '15:33:45'),

  (6, 'Fredericton,NB,CA', '16:34:57'),
  (6, 'Gander,NL,CA', '17:14:06'),
]

# Define start/end times to pull from API
# batch_times = {
#   1: (10, 13),
#   2: (12, 15),
#   3: (13, 16),
#   4: (14, 17),
#   5: (14, 17),
#   6: (15, 18),
# }
batch_times = {i: ('00', '23') for i in range(1,7)}

# These were difficult to get
manual_fill_by_year = pd.DataFrame([
  ("Austin,TX,US", 1996, 10.0, 76.5),
  ("Gander,NL,CA", 2005, 5.0, 48.0),
  ("Houlton,ME,US", 1998, 20.0, 53.0),
  ("Indianapolis,IN,US", 1996, 75.0, 44.0),
], columns=['city', 'year', 'cloud_cover', 'temperature']
)