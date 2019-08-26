import warnings
warnings.filterwarnings('ignore')

import time
import math
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from fbprophet import Prophet
from scipy import stats
from psycopg2 import connect
# import statsmodels.api as sm
import holidays as hol

from psycopg2.extras import execute_values
from psycopg2.extras import DictCursor
from snap_con import get_db_connection
# import seaborn as sns

pd.options.mode.chained_assignment = None
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Query Functions
def query_data(db, query):
    con = connect(get_db_connection(db))
    result = pd.read_sql(query, con)
#     print(f"Data has {result.shape[0]} rows & {result.shape[1]} columns.")
    return result

# Same day - only include payments made on same day of caller
# FALSE includes both same day and scheduled payments
def get_data(from_date, to_date, product_RTO=True, same_day = True):
    
    if same_day:
        condition = 'AND ca.origination_date = ca.payment_dt'
    else:
        condition = ''

    if product_RTO:
        RTO = "="
    else:
        RTO ="<>"
            
    query = """
            SELECT ca.payment_dt AS date
            , SUM(payment_amount) AS dollars_collected
            FROM snapanalytics.collections_arrangements ca
            WHERE ca.arrangement_status = 'VERIFIED'
            AND ca.payment_dt >= '{0}'
            AND ca.payment_dt <= '{1}'
            AND product_type {2} 'RTO'
            {3}
            GROUP BY ca.payment_dt;
            """.format(from_date, to_date, RTO, condition)
    
    result = query_data('aws', query)
    result['date'] = pd.to_datetime(result['date'])
    
    return result

# Metric / other misc functions
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days) + 1


# Returns the date string of one day before
def one_day_before(d_str, ft="%Y-%m-%d"):
    return datetime.strftime(datetime.strptime(d_str, ft) + timedelta(days=-1), ft)


# Function that returns the first day of the current month
def firstDay(curr_dt=datetime.now()):
    return str(curr_dt.year) + '-' + str(curr_dt.month) + '-' + '01'


# Returns last day of current month
def lastDay(curr_dt=datetime.now()):
    return one_day_before(str(curr_dt.year + (curr_dt.month == 12)) + '-' + str(curr_dt.month % 12 + 1) + '-' + '01')


# Removes SNAP holidays from future predictions. Uses holidays package
def removeSnapHolidays(df, test_start_dt):
    yrs = np.unique([x.year for x in df[df['ds'] >= test_start_dt].iloc[:,0]])
    h = hol.US(years=yrs)

    for k,v in list(h.items()):
        if v in ["Washington's Birthday", "Martin Luther King, Jr. Day", "Columbus Day", "Veterans Day",
                "Veterans Day (Observed)"]:
            del h[k]
    dates = pd.Series(list(h))
    df.reset_index(drop=True)
    return df.drop(np.concatenate([np.where(x == df['ds'])[0] for x in dates]))

def holidays():
    # Tax Season (Feb and 5th+ week of year).
    holidays = pd.DataFrame({'holiday': 'taxseason'
                                , 'ds': pd.period_range('2015-01-01', '2050-12-31', freq='D')
                                , 'lower_window': -5
                                , 'upper_window': 5
                             })
    holidays['month'] = getattr(holidays['ds'].dt, 'month')
    holidays['week'] = getattr(holidays['ds'].dt, 'week')
    holidays = holidays[(holidays['month'] == 2) & (holidays['week'] > 5)]
    holidays.drop(['month', 'week'], axis=1, inplace=True)
    holidays['ds'] = holidays['ds'].values.astype('datetime64[M]')
    return holidays

def compute_forecasts(model, start_dt, end_dt, trn_start_dt='2016-01-01', trn_end_dt=None, RTO=True,
                      same_day=False, ret_metrics=False):
    if trn_end_dt is None:
        trn_end_dt = one_day_before(start_dt)

    # Training Data
    collections_data = get_data(from_date=trn_start_dt, to_date=trn_end_dt, product_RTO=RTO, same_day=same_day)
    collections_data = collections_data.rename(columns={"date": "ds", "dollars_collected": "y"})
    collections_data = collections_data[collections_data['y'] > 0]

    # Model Fitting
    model.fit(collections_data)
    # Building Future df
    days_to_forecast = days_between(end_dt, start_dt) + \
                       days_between(start_dt, datetime.strftime(collections_data.iloc[-1,0], '%Y-%m-%d')) - 2
    future = model.make_future_dataframe(periods=days_to_forecast)
    future['Dayofweek'] = getattr(future['ds'].dt, 'dayofweek')

    # Excluding sundays / Observed Holidays
    future = removeSnapHolidays(future, start_dt)
    future = future[future['Dayofweek'] != 6]

    future.drop('Dayofweek', axis=1,inplace=True)

    # Forecasting
    forecast = model.predict(future)
    predictions = forecast[['ds', 'yhat']]
    predictions = predictions[predictions['ds'] >= start_dt]

    # Test Data
    test_data = get_data(from_date=start_dt, to_date=end_dt, product_RTO=RTO, same_day=same_day)
    test_data = test_data.rename(columns={'date' : 'ds', 'dollars_collected' : 'y'})

    # Combining Predictions and actual data
    final_df = pd.merge(predictions, test_data, how='left', on='ds')
    final_df['Predicted_Dollars'] = final_df['yhat'].cumsum()
    final_df['Actual_Dollars'] = final_df['y'].cumsum()
    final_df['Difference'] = final_df['Predicted_Dollars'] - final_df['Actual_Dollars']
    final_df['y'].fillna(0, inplace = True)

    # Returns performance metrics on testing set
    if ret_metrics:
        score_df = final_df[final_df['ds'] < datetime.today().strftime('%Y-%m-%d')]
        score_df['deviations'] = score_df['yhat'] - score_df['y']
        metric_df = pd.Series([round((abs(score_df['deviations'])).mean(), 2),
                               round(math.sqrt(((score_df['deviations']) ** 2).mean()), 2)],
                              index=['mae', 'rmse'])
        return [metric_df, score_df]
    return final_df

def insert_table(query, data):
    con = connect(get_db_connection('aws'))
    cur = con.cursor(cursor_factory=DictCursor)
    execute_values(cur, query, data)

    con.commit()
    cur.close()
    con.close()

def delete_from_table(query):
    con = connect(get_db_connection('aws'))
    cur = con.cursor(cursor_factory=DictCursor)
    cur.execute(query)

    con.commit()
    cur.close()
    con.close()

if __name__ == "__main__":


    ## MODELS ----------------------------------------------------------------------------------------------------------
    # Tuning parameters were determined by cross-validation by training on Jan 2016 - May 2019

    # Dates that are used for predictions. Default is all of current month.
    curr_dt = datetime.now() # + timedelta(days=30)
    START_DATE = firstDay(curr_dt)
    END_DATE = lastDay(curr_dt)

    # MOdel 1: Total Dollars
    model_full = Prophet(seasonality_mode='multiplicative'
                         , seasonality_prior_scale=0.55
                         , changepoint_prior_scale=0.4
                         , yearly_seasonality=13
                         , weekly_seasonality=5
                         , holidays=holidays()
                         , daily_seasonality=False)
    model_full.add_country_holidays(country_name='US')
    model_full.add_seasonality(name='quarterly', period=91, fourier_order=8)

    cf_full = compute_forecasts(model=model_full, start_dt=START_DATE, end_dt=END_DATE, RTO=True,
                                same_day=False)

    # Model 2: Same Day Only
    model_sameDay = Prophet(seasonality_mode='multiplicative'
                            , seasonality_prior_scale=0.04
                            , changepoint_prior_scale=0.05
                            , yearly_seasonality=11
                            , weekly_seasonality=5
                            , holidays=holidays()
                            , daily_seasonality=False)
    model_sameDay.add_country_holidays(country_name='US')

    cf_sameDay = compute_forecasts(model=model_sameDay,  start_dt=START_DATE, end_dt=END_DATE, RTO=True,
                                   same_day=True, ret_metrics=True)

    ## -----------------------------------------------------------------------------------------------------------------
    preds = pd.merge(cf_full[['ds', 'yhat']], cf_sameDay[['ds', 'yhat']], on='ds', how='left')
    preds.columns = ['date', 'Total', 'SameDay']
    preds.iloc[:,-2:] = round(preds.iloc[:,-2:],2)

    preds_arrangement = preds[['date', 'Total']]
    preds_origination = preds[['date', 'SameDay']]

    arr_list = [list(r) for r in preds_arrangement.values]
    orig_list = [list(r) for r in preds_origination.values]

    arr_query = """INSERT INTO snapanalytics.collection_arrangement_prediction (
            date, predicted_dollars)
            VALUES %s"""

    orig_query = """INSERT INTO  snapanalytics.collection_origination_prediction (
            date, predicted_dollars)
            VALUES %s"""

    arr_del_query = "DELETE FROM snapanalytics.collection_arrangement_prediction WHERE date >= '{}' AND date <= '{}'"\
        .format(START_DATE, END_DATE)

    orig_del_query = "DELETE FROM snapanalytics.collection_origination_prediction WHERE date >= '{}' AND date <= '{}'"\
        .format(START_DATE, END_DATE)

    delete_from_table(arr_del_query)
    delete_from_table(orig_del_query)

    insert_table(arr_query, arr_list)
    insert_table(orig_query, orig_list)
