import requests
import sys

import csv
import codecs
import pandas as pd
from io import StringIO, BytesIO
        

YOUR_API_KEY = ''

response = requests.request("GET", f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Salt%20Lake%20City%2C%20UT%2C%20US/2025-03-01/2025-03-09?unitGroup=us&include=days&key={YOUR_API_KEY}&contentType=csv")
if response.status_code!=200:
  print('Unexpected Status code: ', response.status_code)
  sys.exit()  


# Parse the results as CSV
CSVText = csv.reader(response.text.splitlines(), delimiter=',',quotechar='"')
CSVText_list = list(CSVText)

# Example: reading a CSV file with csv.reader
with open("myfile.csv", newline="") as f:
    reader = csv.reader(f)
    data = list(reader)  # convert _csv.reader to a list of lists

# Option 1: First row as header
df = pd.DataFrame(CSVText_list[1:], columns=CSVText_list[0])
df[['datetime', 'tempmax', 'tempmin', 'temp', 'feelslikemin', 'precip', 'preciptype', 'snow', 'snowdepth']]
        