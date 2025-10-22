from dash import Dash, html, dash_table, dcc, callback, Output, Input, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import plotly.graph_objects as go
from datetime import date
from plotly_calplot import calplot
import os

pio.templates.default = "plotly_dark"
pio.renderers.default = "browser"
print(os.getcwd())
# TODO: Figure out why assets folder isn't working properly with the dark dropdown css

# Initialize the app
external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.themes.DARKLY, 'dark_dropdown.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, assets_folder='./weather/dashboards/assets/')

temp_colors = [
    '#3b4cc0', '#528ecb', '#7fb8da', '#b5d5e6', 
    '#e0e0e0',"#e0e0e0", "#e0e0e0", 
    '#f6bfa6', '#ea7b60', '#c63c36', '#962d20',
]
# INPUT DATA
# Create 1/2 index for leap year so we can intepret "hottest day of year" correctly
# This will put Feb 29th between 2-28 and 3-1 in the model
def gen_DoY_index(x, year_type='calendar_year'):
  excess = {
      'calendar_year': 0,
      'water_year': 92,
      'winter_season': 153,
  }[year_type]
  
  mar1_day = 60
  return_value = x.dayofyear

  if x.is_leap_year:
    if x.dayofyear > mar1_day:
      return_value -= 1 
    elif x.dayofyear == mar1_day:
      return_value -= 0.5

  return (return_value - excess - 1) % 365 + 1

def dayofyear_to_month_day(doy):
  dt = pd.Timestamp(f"2025-01-01") + pd.Timedelta(days=doy-1)
  if doy==59.5:
    return "Feb 29"
  return dt.strftime('%b %d')

def str_to_decimal_hr(s):
  h, m = s.split('T')[1].split(':')
  return int(h) + int(m)/60.0

def offset_season(s, offset):
  return str(int(s.split('-')[0]) + offset) + '-' + str(int(s.split('-')[1]) + offset)

N_years = 30 # For normals

temps = pd.read_csv("weather/data_sources/daily_weather.csv", parse_dates=['date'])#.query("date >= '1995-01-01'")
normals = pd.read_csv("weather/output_sources/temp_normals.csv")
sunrise_sunset = pd.read_csv("weather/data_sources/sunrise_set_slc.csv", parse_dates=['time'])

temps['day_of_year'] = temps['date'].apply(gen_DoY_index)
temps['range'] = temps['max_temp'] - temps['min_temp']
temps['year'] = temps['date'].dt.year
temps_minmax = (temps['year'].min(),temps['year'].max())

# add a column rank to temp that ranks how hot each day was relative to all other years
temps['high_rank'] = temps.groupby('day_of_year')['max_temp'].rank(ascending=False, method='min')
temps['low_rank'] = temps.groupby('day_of_year')['min_temp'].rank(ascending=True, method='min')
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
temps['month'] = pd.Categorical(temps['date'].dt.strftime('%b'), categories=month_order, ordered=True)

temps_full = temps.merge(normals.drop(columns=['month'], axis=1), on='day_of_year', how='left', suffixes=('', '_y'))

recent = temps_full[temps_full['date'] >= '2020-01-01']

record_highs = recent[recent['high_rank'] == 1.0]
record_lows = recent[recent['low_rank'] == 1.0]
high_min = recent[recent['low_rank'] == recent['low_rank'].max()]
low_max = recent[recent['high_rank'] == recent['high_rank'].max()]

sunrise_sunset_clean = (
  sunrise_sunset[sunrise_sunset['time'].dt.year == 2024]
  .rename({'time': 'date', 'sunset (iso8601)': 'sunset', 'sunrise (iso8601)': 'sunrise'}, axis=1)
)
sunrise_sunset_clean['sunset_hr'] = sunrise_sunset_clean['sunset'].apply(str_to_decimal_hr)
sunrise_sunset_clean['sunrise_hr'] = sunrise_sunset_clean['sunrise'].apply(str_to_decimal_hr)
sunrise_sunset_clean['day_of_year'] = sunrise_sunset_clean['date'].apply(gen_DoY_index)


# Monthly Heatmap Data
max_date = temps_full['date'].max()
if max_date != max_date + pd.offsets.MonthEnd(0):
  most_recent_month = temps_full['date'].max().replace(day=1) - pd.Timedelta(days=1)
else:
  most_recent_month = max_date

today = date.today()
normal_n_year = 30
years_for_normals = range(date.today().year - normal_n_year, date.today().year)

# Compute Monthly Normals with 30 years; records use all data
month_avgs = (
  temps_full
  .assign(
    for_avg_high = lambda x: x['max_temp'].where(x['year'].isin(years_for_normals), None),
    for_avg_low = lambda x: x['min_temp'].where(x['year'].isin(years_for_normals), None),
    for_avg_temp = lambda x: x['avg_temp'].where(x['year'].isin(years_for_normals), None),
  )
  .groupby(['month'])
  .agg(
    # round these to 1 decimal place
    normal_high=('for_avg_high', lambda x: round(x.mean(), 1)),
    normal_low=('for_avg_low', lambda x: round(x.mean(), 1)),
    normal_temp=('for_avg_temp', lambda x: round(x.mean(), 1)),
    max_temp_p90=('max_temp', lambda x: round(x.quantile(0.9), 1)),
    min_temp_p10=('min_temp', lambda x: round(x.quantile(0.1), 1)),
    record_high=('max_temp', 'max'),
    record_low=('min_temp', 'min'),
    record_high_year=('max_temp', lambda x: temps_full.loc[x.idxmax(), 'date'].date()),
    record_low_year=('min_temp', lambda x: temps_full.loc[x.idxmin(), 'date'].date()),
  )
  .reset_index()
)

monthly_map = (
  pd.melt(
    temps_full[temps_full['date'] <= most_recent_month]\
      [['year', 'month', 'max_temp', 'min_temp', 'avg_temp']],
    id_vars=['year', 'month'],
    value_vars=['max_temp', 'min_temp', 'avg_temp'],
    var_name='metric',
    value_name='temp',
  )
  .groupby(['year', 'month', 'metric'])
  .agg(mean=("temp", "mean"))
  .reset_index()
)

monthly_map_year = (
  monthly_map
  .groupby(['year', 'metric'])
  .agg(
    mean=('mean', 'mean'),
    count=('mean', 'count'),
  )
  .reset_index()
)

monthly_map_year = monthly_map_year[monthly_map_year['count']==12]
monthly_map_year = monthly_map_year.drop(['count'], axis=1)
monthly_map_year['month'] = 'Year'
monthly_map = pd.concat([monthly_map, monthly_map_year])
monthly_map['month'] = pd.Categorical(monthly_map['month'], categories=month_order+["Year"], ordered=True)

monthly_map['rank'] = (
    monthly_map.groupby(['month', 'metric'])['mean']
    .rank(method='min', ascending=True)
)

# Hourly Data
hourly_temp = pd.read_csv("weather/data_sources/hourly_weather.csv", parse_dates=['timestamp'])
hourly_temp['month'] = pd.Categorical(hourly_temp['timestamp'].dt.strftime('%b'), categories=month_order, ordered=True)
hourly_temp['hour'] = hourly_temp['timestamp'].dt.hour
hourly_temp['year'] = hourly_temp['timestamp'].dt.year
hourly_temp['day_of_year']  = hourly_temp['timestamp'].apply(gen_DoY_index)
hourly_temp['precip_chance'] = (hourly_temp['precip'] > 0).astype('int')

hourly_metrics_pretty= {
  'temp': 'Temperature (°F)',
  'humidity': 'Humidity (%)', 
  'wind_speed': 'Wind Speed (mph)',
  'dew_point': 'Dew Point (°F)',
  'precip_chance': 'Precipitation Chance (%)',
  'precip': 'Precipitation (in)',
  'rain': 'Rain (in)',
  'snow': 'Snow (in)',
  'cloud_cover': 'Cloud Cover (%)',
  'pressure': 'Pressure (mb)',
}

season_map = {
  'winter': ['Dec', 'Jan', 'Feb'],
  'spring': ['Mar', 'Apr', 'May'],
  'summer': ['Jun', 'Jul', 'Aug'],
  'fall': ['Sep', 'Oct', 'Nov']
}


hourly_all_metrics = (
  hourly_temp
  .melt(id_vars=['timestamp', 'month', 'hour', 'year', 'day_of_year'], 
         value_vars=hourly_metrics_pretty.keys(),
         var_name='metric_name', value_name='metric_value'
  )
)

hourly_heatmap = (
  hourly_all_metrics
  .groupby(['day_of_year' , 'hour', 'metric_name'])
  .agg(
    metric_value=('metric_value', 'mean'),
  )
  .reset_index()
)
hourly_heatmap['DoY_label'] = hourly_heatmap['day_of_year'].apply(dayofyear_to_month_day)

hourly_all_year = (
  hourly_all_metrics
  .groupby(['year','month' , 'hour', 'metric_name'])
  .agg(
    metric_value=('metric_value', 'mean'),
  )
  .reset_index()
)

hourly_all_mean = (
  hourly_all_year
  .groupby(['month' , 'hour', 'metric_name'])
  .agg(
    metric_value=('metric_value', 'mean'),
  )
  .reset_index()
)
# Season column
hourly_all_mean['season'] = hourly_all_mean['month'].map({v: k for k, vs in season_map.items() for v in vs})
hourly_all_mean_season = (
  hourly_all_mean
  .groupby(['season' , 'hour', 'metric_name'])
  .agg(
    metric_value=('metric_value', 'mean'),
  )
  .reset_index()
)

# Relative to month avg across hour
hourly_all_mean_season['avg_deviation'] = hourly_all_mean_season['metric_value'] - (
  hourly_all_mean_season.groupby(['season', 'metric_name'])['metric_value'].transform('mean')
)

# Precip Data
precip = pd.read_csv('weather/output_sources/precip_table.csv', index_col=False, parse_dates=['date'])

current_year = precip['year'].max()
max_water_year = precip['water_year'].max()
max_winter_year = precip['snow_season'].max()

precip = pd.read_csv('weather/output_sources/precip_table.csv', index_col=False, parse_dates=['date'])
ytd_normals = pd.read_csv('weather/output_sources/ytd_precip_normals.csv')
precip['month'] = pd.Categorical(precip['date'].dt.strftime('%b'), categories=month_order, ordered=True)
precip_data_for_norm = pd.concat([
  precip[precip['year'].between(current_year - N_years, current_year)]\
    .assign(year_type='calendar_year', current_year=current_year, year_for_dash=precip['year']),
  precip[precip['water_year'].between(max_water_year - N_years, max_water_year)]\
    .assign(year_type='water_year', current_year=max_water_year, year_for_dash=precip['water_year']),
  precip[precip['snow_season'].between(offset_season(max_winter_year, - N_years + 1), offset_season(max_winter_year, -1))]\
    .assign(year_type='winter_season', current_year=max_winter_year, year_for_dash=precip['snow_season']),
])

precip_data_for_norm['day_of_year_dash'] = precip_data_for_norm.apply(lambda x: gen_DoY_index(x['date'], x['year_type']), axis=1)

precip_data_for_norm = (
  precip_data_for_norm
  .melt(
    ['date', 'month', 'year_for_dash', 'day_of_year', 'day_of_year_dash', 'year_type', 'current_year'], 
    value_vars=['precip', 'snow', 'rain'], 
    var_name='metric_name', 
    value_name='metric_value')
)

# Temperature Figure
fig = go.Figure()
# Total Temp
fig.add_bar(
    x=recent['date'],
    y=recent['range'],
    base=recent['min_temp'],  # This sets the starting point of each bar
    marker_color='red',
    name='Observed Temperature',
    customdata=recent[['normal_high', 'normal_low']],
    hovertemplate=(
      '<b>Date:</b> %{x}<br><br>' +
      '<b>Observed High:</b> %{y}°F<br>' +
      '<b>Observed Low:</b> %{base}°F<br>' + 
      '<b>Normal High:</b> %{customdata[0]}°F<br>' +
      '<b>Normal Low:</b> %{customdata[1]}°F<br>' +
      '<extra></extra>'  # Removes the default trace info
  )
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
        line=dict(color='red', width=1, dash='dot')
    ),
)
fig.add_trace(
    go.Scatter(
        x=list(recent['date']) + list(recent['date'])[::-1],
        y=list(recent['normal_high']) + list(recent['normal_low'])[::-1],
        fill='toself',
        fillcolor='rgba(125,125,125,0.25)', 
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
        marker=dict(color='royalblue', size=6, symbol='square'),
        name='Coldest High'
    )
)
fig.add_trace(
    go.Scatter(
        x=high_min['date'],
        y=high_min['min_temp'],
        mode='markers',
        marker=dict(color='mediumvioletred', size=6, symbol='square'),
        name='Warmest Low'
    )
)

# Add titles / figsize
fig.update_layout(title="Daily Observed Temperature", xaxis_title='Date', yaxis_title='Temperature (°F)', height=1000, template='plotly_dark')
# Add Slider bar and buttons for year
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
            ]),
            bgcolor='black',
            activecolor='darkred',
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date",
        range=[recent['date'].max() - pd.DateOffset(months=6), recent['date'].max() + pd.DateOffset(days=1)],
    ),
    template='plotly_dark',
)

# Monthly Avg Figure
def monthly_avg_temp():
  fig = go.Figure()
  # Total Temp
  fig.add_bar(
      x=month_avgs['month'],
      y=month_avgs['normal_high'] - month_avgs['normal_low'],
      base=month_avgs['normal_low'],  # This sets the starting point of each bar
      marker_color='red',
      name='Normal',
      customdata=month_avgs[['record_high', 'record_low', 'record_high_year', 'record_low_year']],
      text = month_avgs['normal_high'].astype(str) + '°F',
      textposition='inside',
      hovertemplate=(
        '<b>Month:</b> %{x}<br>' +
        '<b>Avg High:</b> %{y}°F<br>' +
        '<b>Avg Low:</b> %{base}°F<br>' + 
        '<b>Record High:</b> %{customdata[0]}°F (%{customdata[2]})<br>' +
        '<b>Record Low:</b> %{customdata[1]}°F (%{customdata[3]})<br>' +
        '<extra></extra>'
    )
  )
  for i in range(month_avgs.shape[0]):
    fig.add_annotation(
        x=month_avgs['month'][i],
        y=month_avgs['normal_low'][i],
        text=(month_avgs['normal_low'].astype(str) + '°F').tolist()[i],
        showarrow=False,
        yshift=10,  # Adjust vertical position above the bar
    )
  fig.add_trace(
      go.Scatter(
          x=month_avgs['month'], y=month_avgs['record_high'], mode='lines+markers+text', name='Record High', text=month_avgs['record_high'],
          customdata=month_avgs[['record_high_year']],
          hovertemplate='Record High: %{y}°F (%{customdata[0]})<extra></extra>',
          line=dict(color='darkred', width=3)
      ),
  )
  fig.add_trace(
      go.Scatter(
          x=month_avgs['month'], y=month_avgs['record_low'], mode='lines+markers+text', name='Record Low', text=month_avgs['record_low'],
          customdata=month_avgs[['record_low_year']],
          hovertemplate='Record Low: %{y}°F (%{customdata[0]})<extra></extra>',
          line=dict(color='royalblue', width=3)
      ),
  )
  fig.add_trace(
      go.Scatter(
          x=list(month_avgs['month']) + list(month_avgs['month'])[::-1],
          y=list(month_avgs['max_temp_p90']) + list(month_avgs['min_temp_p10'])[::-1],
          fill='toself',
          fillcolor='rgba(125,125,125,0.25)', 
          line_color='rgba(255,255,255,0)',
          showlegend=True,
          name='10-90th percentile',
          hoverinfo="skip",
      ),
  )
  fig.add_vline(
      x=today.strftime("%b"),
      line_width=2,
      line_dash="dash",
      line_color='rgba(125,125,125,0.25)',
  )
  fig.update_layout(
    xaxis_title='Month', 
    yaxis_title='Temperature (°F)',
    paper_bgcolor='#333333', # figure
    plot_bgcolor="#222222", # plot area
  )
  return fig

dbc_row_col = lambda x, width=12: dbc.Row(children=[dbc.Col([x], width=width)])
first_col_width = 7

# Dash layout
app.layout = dbc.Container([
  dbc.Tabs([
    dcc.Tab(label='Temperature', children=[
      dbc.Row([
        html.Div("Temperature Dashboard")
      ]),
      dbc.Row([
        dcc.Graph(figure=fig, id='observed_temp_line')
      ]),
    ]),
    dcc.Tab(label='Departure from Normal', children = [
      dbc_row_col(html.Div("Select metric for heatmaps:"), width=first_col_width),
      dbc_row_col(
        dcc.Dropdown(
          options={
            'max_temp': 'High Temperature',
            'min_temp':'Low Temperature', 
            'avg_temp': 'Mean Temperature',
          },
          value='max_temp',
          style={"color": "#000000"},
          id='daily_heatmap_dropdown',
        ), width=first_col_width
      ),
      dbc_row_col(html.Div("Select start for 5-year range (daily only):"), width=first_col_width),
      dbc_row_col(
          dcc.Slider(
              min=int(round(temps_minmax[0]/10)*10),
              max=temps_minmax[1],
              step=1,
              id='heatmap-year-slider',
              value=2021,
              marks={str(year): str(year) for year in range(int(round(temps_minmax[0]/10)*10), temps_minmax[1]+1, 5)},
              tooltip={"placement": "bottom", "always_visible": True},
              included=False,
          ), width=first_col_width         
      ),
      dbc.Row([
        dbc.Col([
          html.Div(children="Daily Temperature Deviation from Normal", style={'fontSize': 24}),
        ], width=first_col_width),
        dbc.Col([
          html.Div(children="Monthly Normals", style={'fontSize': 24}),
        ], width=12-first_col_width),
      ]),
      dbc.Row([
        dbc.Col([
          dcc.Graph(figure={}, id='calendar_heatmap')
        ], width=first_col_width),
        dbc.Col([
          dcc.Graph(figure=monthly_avg_temp(), id='monthly_avg_temp')
        ], width=12-first_col_width),
      ]),
      dbc_row_col(html.Div("Monthly Temperature Rank (1 = Coldest)", style={'fontSize': 24}), width=first_col_width),
      dbc_row_col(
        dcc.Graph(figure={}, id='monthly_temp_heatmap'), width=first_col_width
      ),
    ]),
    dcc.Tab(label='Hourly', children=[
      dbc_row_col(html.Div("Select metric for hourly plots:")),
      dbc_row_col(
        dcc.Dropdown(
          options=hourly_metrics_pretty,
          value='temp',
          style={"color": "#000000"},
          id='hourly_monthly_input',
        )
      ),
      dbc_row_col(html.Div("Hourly Average by Month", style={'fontSize': 24})),
      dbc_row_col(dcc.Graph(figure={}, id='hourly_monthly_scatter')),
      dbc_row_col(html.Div("30-Year Hourly Average", style={'fontSize': 24})),      
      dbc_row_col(dcc.Graph(figure={}, id='hourly_heatmap')),
      dbc.Row([
        dbc.Col([
          html.Div(children="Seasonal Hourly Average", style={'fontSize': 24}),
        ], width=6),
        dbc.Col([], width=6),
      ]),
      dbc.Row([
        dbc.Col([
          dcc.Graph(figure={}, id='hourly_season'),
        ], width=6),
        dbc.Col([
          dcc.Graph(figure={}, id='hourly_season_deviation'),
        ], width=6),        
      ]),
    ]),
    dcc.Tab(label='Precipitation', children=[
      dbc_row_col(html.Div("Select precipitation metric:")),
      dbc_row_col(
        dcc.Dropdown(
          options={
            'precip': 'Total Precipitation (in)',
            'rain': 'Rainfall (in)', 
            'snow': 'Snowfall (in)',
          },
          value='precip',
          style={"color": "#000000"},
          id='precip_metric_dropdown',
        ),
      ),
      dbc_row_col(html.Div("Select Year Type:")),
      dbc_row_col(
        dcc.Dropdown(
          options={
            'calendar_year': 'Calendar Year (Jan-Dec)',
            'water_year': 'Water Year (Oct-Sep)', 
            'snow_season': 'Snow Season (Aug-Jul)',
          },
          value='calendar_year',
          style={"color": "#000000"},
          id='water_calendar_dropdown',
        ),
      ),
      dbc_row_col(html.Div("Year to Date Precipitation vs. Normals", style={'fontSize': 24})),
      dbc_row_col(dcc.Graph(figure={}, id='ytd_precip_chart'), width=6),
    ]),
  ]),
], fluid=True)

# Callbacks

# Daily Heatmap
@callback(
    Output(component_id='calendar_heatmap', component_property='figure'),
    Input(component_id='daily_heatmap_dropdown', component_property='value'),
    Input(component_id='heatmap-year-slider', component_property='value')
)
def update_graph(metric_chosen, year_start):

  heatmap_df = temps_full[temps_full['year'].between(year_start, year_start+4)].copy()
  heatmap_df['departure'] = {
    'max_temp': heatmap_df['max_temp'] - heatmap_df['normal_high'],
    'min_temp': heatmap_df['min_temp'] - heatmap_df['normal_low'],
    'avg_temp': heatmap_df['avg_temp'] - heatmap_df['normal_temp'],
  }[metric_chosen]

  fig_heatmap = calplot(
      heatmap_df,
      x="date",
      y="departure",
      text=metric_chosen,
      # texttemplate="%{text}°F",
      month_lines=True,
      month_lines_color='#333333',
      month_lines_width=3.5,
      colorscale=temp_colors,
      years_title=True,
      showscale=True,
      cmap_min=-20,
      cmap_max=20,
      total_height=175*5,
      dark_theme=True,
      space_between_plots=0.04,
  )
  fig_heatmap.update_layout(
    # paper_bgcolor='#222222', # figure
    # plot_bgcolor='#222222', # plot area
  )

  return fig_heatmap


@callback(
    Output(component_id='monthly_temp_heatmap', component_property='figure'),
    Input(component_id='daily_heatmap_dropdown', component_property='value'),
)
def update_monthly_heatmap(metric_chosen):

  data_for_temp_heatmap = monthly_map[monthly_map['metric']==metric_chosen]

  fig = go.Figure(data=go.Heatmap(
      x=data_for_temp_heatmap['year'],
      y=data_for_temp_heatmap['month'],
      z=data_for_temp_heatmap['rank'],
      colorscale=temp_colors,
      zmin=1,
      xgap=1,
      ygap=1,
      zmax=data_for_temp_heatmap['rank'].max(),
      connectgaps=False,
      customdata=data_for_temp_heatmap[['mean',]],
      texttemplate="%{z}",
      hovertemplate=(
        '%{y} %{x}:' +
        '<br>Rank: %{z}' +
        f'<br>Avg({metric_chosen}): %{{customdata[0]:.1f}}°F' +
        '<extra></extra>'  # Removes the default trace info
    ),
  ))
  fig.update_layout(
      # title=f'Monthly Temperature Rank',
      xaxis_title='Year',
      yaxis=dict(title='Month',autorange='reversed'),
      height=600,
      # width=1420,
      paper_bgcolor='#333333',
      plot_bgcolor='#333333',
      margin=dict(l=20, r=20, t=20, b=20),
  )
  
  return fig

# Monthly Hourly Scatter
@callback(
    Output(component_id='hourly_monthly_scatter', component_property='figure'),
    Input(component_id='hourly_monthly_input', component_property='value'),
)
def update_monthly_heatmap(metric_name):
  fig = make_subplots(
    rows=1, cols=len(month_order), subplot_titles=month_order, shared_yaxes=True, horizontal_spacing=0.004,
    y_title=hourly_metrics_pretty[metric_name],
    x_title='Time of Day',
  )

  for i, month in enumerate(month_order):
    month_hour = hourly_all_year[(hourly_all_year['month']==month)&(hourly_all_year['metric_name']==metric_name)]
    month_mean = hourly_all_mean[(hourly_all_mean['month']==month)&(hourly_all_mean['metric_name']==metric_name)]

    fig.add_trace(
        go.Scatter(
            x=month_hour['hour'], 
            y=month_hour['metric_value'], 
            mode='markers', 
            name='Observed Month Avg', 
            marker=dict(size=4, color='red', opacity=0.3),
            # line=dict(width=1, dash='dot', color='rgba(255, 0, 0, 0.25)'),
            customdata=month_hour[['year', 'month']],
            hovertemplate=(
                "<b>%{customdata[1]} %{customdata[0]}</b><br>" +
                "<b>Hour: %{x}:00</b><br>"+
                f"<b>{hourly_metrics_pretty[metric_name]}: %{{y:.2f}}</b><br>"+
                "<extra></extra>"
            ),
            showlegend=(i==0),
            legendgroup='Group A',
        ), row=1, col=i+1
    )
    fig.add_trace(
        go.Scatter(
            x=month_mean['hour'], y=month_mean['metric_value'], mode='lines', name='Mean', line=dict(color='red', width=4),
            hovertemplate=(
            "<b>Hour: %{x}:00</b><br>"+
            f"<b>{hourly_metrics_pretty[metric_name]}: %{{y:.2f}}</b><br>"+
            "<extra></extra>"
            ),
            showlegend=(i==0),
            legendgroup='Group B',
        ), row=1, col=i+1
    )
  fig.update_layout(
      # title=f'Hourly Temperature for {month}',
      paper_bgcolor='#333333', # figure
      plot_bgcolor="#222222", # plot area
      height=800,
      legend=dict(
          orientation="h",
          yanchor="bottom",
          y=-0.10,
          xanchor="center",
          x=0.05,
      ),
  )

  return fig

# Seasonal Hourly Avg
@callback(
    Output(component_id='hourly_season', component_property='figure'),
    Input(component_id='hourly_monthly_input', component_property='value'),
)
def update_hourly_season(metric_name):
  data = hourly_all_mean_season[hourly_all_mean_season['metric_name']==metric_name]
  fig = px.line(
    data,
    x='hour', y='metric_value', color='season', color_discrete_map = {
      'winter': 'royalblue',
      'spring': 'green',
      'summer': 'gold',
      'fall': 'red',
    },
  )
  fig.update_traces(
    hovertemplate=("<b>Season: %{customdata[0]}</b><br>" +
      "<b>Hour:</b> %{x}<br>" +
      f"<b>{hourly_metrics_pretty[metric_name]}:</b> %{{y:.6f}}<extra></extra>"
    ),
    customdata=data[['season']],
  )
  fig.update_layout(
    paper_bgcolor='#333333', # figure
    plot_bgcolor="#222222", # plot area
    height=500,
    xaxis_title='Time of Day',
    yaxis_title=hourly_metrics_pretty[metric_name],
)
  return fig

# Seasonal avg adjusted
@callback(
    Output(component_id='hourly_season_deviation', component_property='figure'),
    Input(component_id='hourly_monthly_input', component_property='value'),
)
def update_hourly_season(metric_name):
  fig = px.line(
    hourly_all_mean_season[hourly_all_mean_season['metric_name']==metric_name],
    x='hour', y='avg_deviation', color='season', color_discrete_map = {
      'winter': 'royalblue',
      'spring': 'green',
      'summer': 'gold',
      'fall': 'red',
    },
  )
  fig.update_layout(
    paper_bgcolor='#333333', # figure
    plot_bgcolor="#222222", # plot area
    height=500,
    xaxis_title='Time of Day',
    yaxis_title=hourly_metrics_pretty[metric_name] + " Deviation from Avg",
)
  return fig

# Hourly heatmap
@callback(
    Output(component_id='hourly_heatmap', component_property='figure'),
    Input(component_id='hourly_monthly_input', component_property='value'),
)
def update_hourly_heatmap(metric_chosen):
  data_for_temp_heatmap = (
    hourly_heatmap[hourly_heatmap['metric_name']==metric_chosen]
  ).query("day_of_year != 59.5")

  fig = go.Figure(data=go.Heatmap(
      x=data_for_temp_heatmap['day_of_year'],
      y=data_for_temp_heatmap['hour'],
      z=data_for_temp_heatmap['metric_value'],
      customdata=data_for_temp_heatmap[['DoY_label']],
      colorscale='turbo',
      connectgaps=False,
      hovertemplate=(
        '<br>Day of Year: %{customdata[0]}' +
        '<br>Hour: %{y}:00' +
        f'<br>Avg({metric_chosen})=%{{z}}' +
        '<extra></extra>'
    ),
  ))
  fig.add_trace(
    go.Scatter(
        x=sunrise_sunset_clean['day_of_year'], 
        y=sunrise_sunset_clean['sunset_hr'], 
        mode='lines', 
        line=dict(color='black', width=0.5, dash='dot'), 
        showlegend=False,
        hovertemplate=(
          '<br>sunset: %{y:.2f}' +
          '<extra></extra>'
        )        
    )
  )
  fig.add_trace(
    go.Scatter(
        x=sunrise_sunset_clean['day_of_year'], 
        y=sunrise_sunset_clean['sunrise_hr'], 
        mode='lines',
        line=dict(color='black', width=0.5, dash='dot'),
        showlegend=False,
        hovertemplate=(
          '<br>sunrise: %{y:.2f}' +
          '<extra></extra>'
        )
    )    
  )
  fig.update_layout(
      # title=f'Monthly Temperature Rank',
      xaxis_title='Day of Year',
      yaxis_title='Time of Day',
      height=500,
      # width=1420,
      paper_bgcolor='#333333',
      plot_bgcolor='#333333',
      margin=dict(l=20, r=20, t=20, b=20),
  )
  return fig

# Precip Dash
@callback(
    Output(component_id='ytd_precip_chart', component_property='figure'),
    Input(component_id='water_calendar_dropdown', component_property='value'),
    Input(component_id='precip_metric_dropdown', component_property='value'),
)
def precip_ytd_chart(calendar_type, metric):
  ytd = (
    precip_data_for_norm
    .fillna({"metric_value": 0})
    .query(f"(metric_name == '{metric}') & (year_type == '{calendar_type}')")
    .sort_values(by=['year_type', 'metric_name', 'year_for_dash', 'date'])
    .groupby(['year_type', 'metric_name', 'year_for_dash'])
    .apply(lambda x: x.assign(year_to_date_precip=x['metric_value'].cumsum()))
    .reset_index(drop=True)
    .sort_values(by=['year_type', 'metric_name', 'year_for_dash', 'day_of_year_dash'])
  )

  current_year_ytd = ytd.query("year_for_dash == current_year")
  chart_label = current_year_ytd['current_year'].head().iloc[0]

  ytd_avg = (
    ytd_normals
    .query(f"(metric_name == '{metric}') & (year_type == '{calendar_type}')")
  )

  fig = px.line(ytd.query(f"(year_for_dash != current_year) & (year_type == '{calendar_type}')"), x='day_of_year_dash', y='year_to_date_precip', color='year_for_dash')
  fig.update_traces(
      line=dict(color='rgb(144, 238, 144, 0.25)', width=0.75, dash='dot'),
      selector=dict(mode='lines')  # Ensure it applies only to line traces
  )
  fig.add_scatter(x=current_year_ytd['day_of_year_dash'], y=current_year_ytd['year_to_date_precip'], mode='lines', name=chart_label, line=dict(color='rgb(50, 255, 210)', width=2))
  fig.add_scatter(x=ytd_avg['day_of_year_dash'], y=ytd_avg['avg_precip_ytd'], mode='lines', name='Average', line=dict(color='green', width=4))
  fig.add_traces([
      go.Scatter(
          x=list(ytd_avg['day_of_year_dash']) + list(ytd_avg['day_of_year_dash'])[::-1],
          y=list(ytd_avg['p75_precip_ytd']) + list(ytd_avg['p25_precip_ytd'])[::-1],
          fill='toself',
          fillcolor='rgba(0, 200, 0, 0.25)',
          line=dict(color='rgba(255,255,255,0)'),
          hoverinfo="skip",
          name='25th-75th Percentile',
      )
  ])
  fig.update_layout(
    height=800, 
    xaxis_title='Day of Year', 
    yaxis_title=metric, 
    paper_bgcolor='#333333', 
    plot_bgcolor="#222222"
  )
  return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8052)