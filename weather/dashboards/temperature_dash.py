import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

pio.renderers.default = "browser"

# Create 1/2 index for leap year so we can intepret "hottest day of year" correctly
# This will put Feb 29th between 2-28 and 3-1 in the model
def gen_DoY_index(x):
  if x.is_leap_year:
    if x.dayofyear > 60:
      return x.dayofyear - 1
    elif x.dayofyear==60:
      return x.dayofyear - 0.5
  return x.dayofyear

temps = pd.read_csv("weather/data_sources/daily_weather.csv", parse_dates=['date'])
normals = pd.read_csv("weather/output_sources/temp_normals.csv")

temps['day_of_year'] = temps['date'].apply(gen_DoY_index)
temps['range'] = temps['max_temp'] - temps['min_temp']
recent = temps[temps['date'] >= '2024-09-01'].merge(normals, on='day_of_year', how='left')

from plotly.subplots import make_subplots
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=("Daily Max Temperatures vs Normal High (2025)", 
                                    "Daily Min Temperatures vs Normal Low (2025)",
                                    "Daily Temperature Range (2025)")
)
# fig.layout.template = 'plotly_dark'

fig.add_trace(go.Scatter(
    x=list(recent['date']) + list(recent['date'])[::-1],
    y=list(recent['max_temp_p90']) + list(recent['max_temp_p10'])[::-1],
    fill='toself',
    fillcolor='rgba(139,0,0,0.2)',
    line_color='rgba(255,255,255,0)',
    showlegend=True,
    name='10-90th Percentile',
    hoverinfo="skip"),
    row=1, col=1
  )
fig.add_trace(
  go.Scatter(
    x=recent['date'], y=recent['max_temp'], mode='lines+markers', name='Observed High Temp',
    line=dict(color='red', width=2),
  ),
  row=1, col=1
)
fig.add_trace(
  go.Scatter(
    x=recent['date'], y=recent['normal_high'], mode='lines', name='Normal High Temp',
    line=dict(color='darkred', width=4),

  ),
  row=1, col=1
)

# Min Temp
fig.add_trace(
    go.Scatter(
        x=list(recent['date']) + list(recent['date'])[::-1],
        y=list(recent['min_temp_p90']) + list(recent['min_temp_p10'])[::-1],
        fill='toself',
        fillcolor='rgba(0,0,200,0.2)',  # Dark blue with alpha=0.2
        line_color='rgba(255,255,255,0)',
        showlegend=True,
        name='10-90th Percentile',
        hoverinfo="skip",
    ),
    row=2, col=1
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['min_temp'], mode='lines+markers', name='Observed Low Temp',
        line=dict(color='dodgerblue', width=2)
    ),
    row=2, col=1
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['normal_low'], mode='lines', name='Normal Low Temp',
        line=dict(color='blue', width=4)
    ),
    row=2, col=1
)

fig.add_bar(
    x=recent['date'],
    y=recent['range'],
    base=recent['min_temp'],  # This sets the starting point of each bar
    marker_color='red',
    name='Temperature Range',
    row=3, col=1
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['normal_temp'], mode='lines', name='Seasonal Normal',
        line=dict(color='darkred', width=3)
    ),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['min_temp_p10'], mode='lines', name='10th percentile Low',
        line=dict(color='blue', width=1, dash='dot')
    ),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['max_temp_p90'], mode='lines', name='90th Percentile High',
        line=dict(color='darkred', width=1, dash='dot')
    ),
    row=3, col=1
)


fig.update_layout(title='Temperatures (2025)', xaxis_title='Date', yaxis_title='Temperature (°F)', height=1600)
fig.show()