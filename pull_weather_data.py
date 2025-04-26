import requests
from io import StringIO, BytesIO
from pandas import read_csv

# https://www.visualcrossing.com/resources/documentation/weather-api/weather-api-documentation/

YOURAPIKEY = ''
start_time = '2024-04-08T12:00:00'
end_time = '2024-04-08T17:00:00'


cities = [
    # 10a - 2p
    'Mazatlan,MX',
    'Torreon,MX',
    # 12p - 4p
    'San Antonio,TX,US',
    'Austin,TX,US',
    'Fort Worth,TX,US',
    'Dallas,TX,US',
    'Little Rock,AR,US',
    # 1p - 5p
    'Carbondale,IL,US',
    'Indianapolis,IN,US',
    'Dayton,OH,US',
    'Cleveland,OH,US'
    'Erie,PA,US',
    # 2p - 6p
    'Buffalo,NY,US',
    'Rochester,NY,US',
    'Burlington,VT,US',
    'Houlton,ME,US',
    'Gander,NL,CA',
]

location = '|'.join(cities[3:8])

weather_request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?&aggregateHours=1&startDateTime={start_time}&endDateTime={end_time}&unitGroup=us&contentType=csv&location={location}&key={YOURAPIKEY}"
response = requests.get(weather_request)
response

df = read_csv(BytesIO(response.content), header=0)
df[['Address', 'Date time','Temperature', 'Cloud Cover', 'Conditions', ']]


15*4*20


