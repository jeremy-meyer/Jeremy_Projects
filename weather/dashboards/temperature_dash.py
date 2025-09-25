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

temps = pd.read_csv("weather/data_sources/daily_weather.csv", parse_dates=['date'])#.query("date >= '1995-01-01'")
normals = pd.read_csv("weather/output_sources/temp_normals.csv")

temps['day_of_year'] = temps['date'].apply(gen_DoY_index)
temps['range'] = temps['max_temp'] - temps['min_temp']

# add a column rank to temp that ranks how hot each day was relative to all other years
temps['high_rank'] = temps.groupby('day_of_year')['max_temp'].rank(ascending=False, method='min')
temps['low_rank'] = temps.groupby('day_of_year')['min_temp'].rank(ascending=True, method='min')

recent = temps[temps['date'] >= '2020-01-01'].merge(normals, on='day_of_year', how='left')

record_highs = recent[recent['high_rank'] == 1.0]
record_lows = recent[recent['low_rank'] == 1.0]
high_min = recent[recent['low_rank'] == recent['low_rank'].max()]
low_max = recent[recent['high_rank'] == recent['high_rank'].max()]

fig = go.Figure()
# Total Temp
fig.add_bar(
    x=recent['date'],
    y=recent['range'],
    base=recent['min_temp'],  # This sets the starting point of each bar
    marker_color='red',
    name='Observed Temperature',
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['normal_temp'], mode='lines', name='Seasonal Normal',
        line=dict(color='darkred', width=3)
    ),
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['min_temp_p10'], mode='lines', name='10th percentile Low',
        line=dict(color='blue', width=1, dash='dot')
    ),
)
fig.add_trace(
    go.Scatter(
        x=recent['date'], y=recent['max_temp_p90'], mode='lines', name='90th Percentile High',
        line=dict(color='darkred', width=1, dash='dot')
    ),
)
fig.add_trace(
    go.Scatter(
        x=list(recent['date']) + list(recent['date'])[::-1],
        y=list(recent['normal_high']) + list(recent['normal_low'])[::-1],
        fill='toself',
        fillcolor='rgba(100,100,100,0.2)', 
        line_color='rgba(255,255,255,0)',
        showlegend=True,
        name='Normal',
        hoverinfo="skip",
    ),
)
fig.add_trace(
    go.Scatter(
        x=record_highs['date'],
        y=record_highs['max_temp'],
        mode='markers',
        marker=dict(color='darkred', size=8, symbol='diamond'),
        name='Record High'
    )
)

fig.add_trace(
    go.Scatter(
        x=record_lows['date'],
        y=record_lows['min_temp'],
        mode='markers',
        marker=dict(color='blue', size=8, symbol='diamond'),
        name='Record Low'
    )
)
fig.add_trace(
    go.Scatter(
        x=low_max['date'],
        y=low_max['max_temp'],
        mode='markers',
        marker=dict(color='royalblue', size=8, symbol='square'),
        name='Coldest High'
    )
)
fig.add_trace(
    go.Scatter(
        x=high_min['date'],
        y=high_min['min_temp'],
        mode='markers',
        marker=dict(color='mediumvioletred', size=8, symbol='square'),
        name='Warmest Low'
    )
)

fig.update_layout(title="Daily Observed Temperature", xaxis_title='Date', yaxis_title='Temperature (°F)', height=1000)

fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=3,
                     label="3m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date",
        range=[recent['date'].max() - pd.DateOffset(months=6), recent['date'].max()]
    )
)


fig.show()
