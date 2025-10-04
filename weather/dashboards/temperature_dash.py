from dash import Dash, html, dash_table, dcc, callback, Output, Input, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
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
      name='Monthly Normal',
      customdata=month_avgs[['record_high', 'record_low']],
      hovertemplate=(
        '<b>Month:</b> %{x}<br>' +
        '<b>Avg High:</b> %{y}°F<br>' +
        '<b>Avg Low:</b> %{base}°F<br>' + 
        '<b>Record High:</b> %{customdata[0]}°F<br>' +
        '<b>Record Low:</b> %{customdata[1]}°F<br>' +
        '<extra></extra>'
    )
  )
  fig.add_trace(
      go.Scatter(
          x=month_avgs['month'], y=month_avgs['record_high'], mode='lines+markers', name='Record High', text='record_high',
          line=dict(color='darkred', width=3)
      ),
  )
  fig.add_trace(
      go.Scatter(
          x=month_avgs['month'], y=month_avgs['record_low'], mode='lines+markers', name='Record Low', text='record_low',
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
  fig.update_layout(xaxis_title='Month', yaxis_title='Temperature (°F)')
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
      dbc_row_col(html.Div("Select metric for heatmaps:")),
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
        )
      ),
      dbc_row_col(html.Div("Select start for 5-year range (daily only):")),
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
          )         
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
  # fig_heatmap.update_layout(width=1420)

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
      paper_bgcolor='#222222',
      plot_bgcolor='#222222',
      margin=dict(l=20, r=20, t=20, b=20),
  )
  
  return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8052)