# Python script that builds timeseries prophet models (72) for each merchant user
# and predicts the total number of product sales. Tests results for previous month
# and predicts for future month.
# Script packages results in a csv file and sends it via email. 

import warnings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from fbprophet import Prophet
from psycopg2 import connect
import copy
from snap_con import get_db_connection
import matplotlib.pyplot as plt

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None
pd.set_option('display.float_format', lambda x: '%.3f' % x)


def query_data(db, query):
    con = connect(get_db_connection(db))
    result = pd.read_sql(query, con)
#     print(f"Data has {result.shape[0]} rows & {result.shape[1]} columns.")
    return result

# Completed end date: where to truncate data (so we don't have incomplete months)
def get_data(compl_end_dt):
    # moving_window_query = """
    #     SELECT ca.ae_user,DATE_TRUNC('months',complete_ts::DATE)::DATE AS month,COUNT(*) AS origs
    #       FROM snapanalytics.curated_applications ca
    #       LEFT JOIN snapanalytics.merchant m ON m.merchant_id = ca.merchant_id
    #       WHERE complete_ts < '{}'
    #       AND complete_ts::DATE > (m.application_signed_dt::DATE + INTERVAL '90 Days')
    #       AND merchant_status != 'INACTIVE'
    #       GROUP BY ca.ae_user,month
    #       order by ae_user, month
    # """.format(compl_end_dt)

    fixed_window_query = """
        SELECT ca.ae_user,DATE_TRUNC('months',complete_ts::DATE)::DATE AS month,COUNT(*) AS origs
         FROM snapanalytics.curated_applications ca
         LEFT JOIN snapanalytics.merchant m ON m.merchant_id = ca.merchant_id
         WHERE complete_ts < '{}'
         AND complete_ts::DATE >= (DATE_TRUNC('months',m.application_signed_dt::DATE + INTERVAL '90 Days')::DATE + INTERVAL '1 month')
         AND merchant_status != 'INACTIVE'
         GROUP BY ca.ae_user,month  
    """.format(compl_end_dt)

    curated_apps = pd.DataFrame(query_data('aws', fixed_window_query))
    curated_apps['month'] = pd.to_datetime(curated_apps['month'], utc=True).values.astype('datetime64[M]')
    curated_apps.rename(axis=1, mapper={'month': 'ds', 'origs': 'y'}, inplace=True)
    curated_apps.sort_values(by=['ae_user', 'ds'], axis=0, inplace=True)

    return curated_apps


def months_between(d1, d2):
    # Inaccurate as distance gets larger between months
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return int(np.floor((abs((d2 - d1).days)+2)/30))


def firstDay(curr_dt=datetime.now()):
    return str(curr_dt.year) + '-' + str(curr_dt.month) + '-' + '01'


def reformatDateString(dt, ft):
    return datetime.strftime(datetime.strptime(dt, '%Y-%m-%d'), ft)

def holidays():
    # Tax Season (Feb) and Holiday Season (Dec)
    holidays = pd.DataFrame({'holiday': 'Holiday_Season'
                                , 'ds': pd.period_range('2012-12-01', '2050-12-01', freq='M')
                                , 'lower_window': 0
                                , 'upper_window': 0
    })
    holidays['month'] = getattr(holidays['ds'].dt, 'month')
    holidays = holidays[(holidays['month'] == 12) | (holidays['month'] == 2)]
    holidays[holidays['month'] == 2] = holidays[holidays['month'] == 2].replace({'Holiday_Season': 'Tax Season'})
    holidays.drop(['month'], axis=1, inplace=True)
    holidays['ds'] = holidays['ds'].values.astype('datetime64[M]')
    return holidays


# Returns data(from df) for a given name
def get_name_data(df, name):
    return df[df['ae_user'] == name]


# Returns valid names for prediction and a separate list for names that failed the 1st and 2nd conditions
def get_names(df, test_dt, min_datapoints=10, max_month_before_test=0):
    names = np.unique(df['ae_user'])
    dat_inds = np.array([get_name_data(df, x).shape[0] for x in names]) >= min_datapoints
    mon_inds = np.array([months_between(get_name_data(df, x).iloc[-1, np.where(df.columns == 'ds')[0][0]].
                                        strftime('%Y-%m-%d'), test_dt) for x in names]) <= max_month_before_test
    return names[dat_inds * mon_inds], [names[~dat_inds], names[~mon_inds]]


# Computes a single forecast from a given df and model
def compute_forecast(model, df, test_dt='2019-07-01', trn_beg_dt='2010-01-01',
                      ret_metrics=False, verbose=False, plotit=False):
    # Training Data
    collections_data = df[(df['ds'] < test_dt) & (df['ds'] >= trn_beg_dt)]
    collections_data = collections_data[collections_data['y'] > 0]
    trn_end_dt = collections_data['ds'].iloc[-1]

    # Model Fitting / Months at a time
    model.fit(collections_data)
    future = model.make_future_dataframe(periods=months_between(test_dt, trn_end_dt.strftime('%Y-%m-%d')), freq='M')

    # Forecasting
    forecast = model.predict(future)
    predictions = forecast[['ds', 'yhat']]
    predictions = predictions[predictions['ds'] > trn_end_dt]
    # print(predictions)

    pred_val = predictions['yhat'].values[-1]
    pred_val = round(pred_val * (pred_val > 0) + (pred_val <= 0), 0)  # Positive predictions & round to integer count
    test_set = df[df['ds'] == test_dt]
    test_exists = len(test_set) != 0

    if verbose:
        if test_exists:
            print(f"\nError: ${pred_val - test_set['y'].values[0]}")
            print(f"Predicted: ${round(predictions['yhat'].values[0],1)}")
            print(f"Actual: ${test_set['y'].values[0]}")
        else:
            print('\n No Testing data available')

    # Visual of model results
    if plotit:
        model.plot(forecast)
        if test_exists:
            plt.scatter(datetime.strptime(test_dt, "%Y-%m-%d"), test_set['y'].values[0], color='r')
        # model.plot_components(forecast)

    # If you want to return the prediction accuracy metrics
    if ret_metrics:
        test_set = df[df['ds'] == test_dt]
        if test_exists:
            metric_df = pd.Series([test_set['y'].values[0],
                                   round(pred_val, 1),
                                   pred_val - test_set['y'].values[0]],
                                  index=['y', 'yhat', 'Error'])
        else:
            metric_df = pd.Series([float('nan'),
                                   round(pred_val, 1),
                                   float('nan')],
                                  index=['y', 'yhat', 'Error'])

        return metric_df
    return pred_val


# df is a dataframe containing all the data (test+train). Make sure it is sorted by user, then ascending date order
# prediction_dt is the date you wish to predict for (this will become the "test set")
# test_metrics determines if you want to generate testing set metrics. Leave false for predictions only!
def forecast_all_users(df, prediction_dt, test_metrics=False, print_loading=False):

    names = get_names(df, prediction_dt, max_month_before_test=1-int(test_metrics))[0]
    preds = pd.DataFrame(np.zeros([len(names), 1 + test_metrics*2]))
    h = holidays()

    # The Model---------------------------------------------------
    model = Prophet(seasonality_mode='multiplicative'
                    , holidays=h
                    , daily_seasonality=False, weekly_seasonality=False
                    ,seasonality_prior_scale=10
                    ,yearly_seasonality=5
                    ,holidays_prior_scale=1
                    ,changepoint_prior_scale=.15
                    ,n_changepoints=10
                    ,changepoint_range=.85)
    # model_full.add_seasonality(name='quarterly', period=91, fourier_order=8)
    # -------------------------------------------------------------

    for i in range(len(names)):
        dat = get_name_data(df, names[i])
        cf = compute_forecast(copy.deepcopy(model), df=dat, test_dt=prediction_dt, ret_metrics=test_metrics)
        if test_metrics:
            preds.iloc[i] = cf.values
        else:
            preds.iloc[i] = cf
        if print_loading and ((i+1) % 10 == 0):
            print("Finished {} out of {}\n".format(i + 1, len(names)))

    results = pd.concat([pd.Series(names).reset_index(drop=True), pd.DataFrame(preds)], ignore_index=True, axis=1)

    if test_metrics:
        results.columns = ['Name', 'Actual', 'Predicted', 'Error']
        results['Percent Error'] = results['Error']/results['Actual']

        # print('\nMedian Absolute Percent Error: {} %'.
              #format(100*round(np.nanmedian(abs(results[['Percent Error']])),4)))
        # print('Median Absolute Error: {}'.format(np.nanmedian(abs(results[['Error']]))))
        # print('Mean Absolute Error: {}'.format(round(np.nanmean(abs(results[['Error']])),3)))
    else:
        results.columns = ['Name', 'Future Prediction']
    return results


if __name__ == "__main__":
    prediction_date = firstDay()
    testing_date = firstDay(datetime.strptime(prediction_date, "%Y-%m-%d") - timedelta(days=1))

    dat = get_data(prediction_date)
    names_ignored = np.unique(np.concatenate(get_names(dat, testing_date)[1]))  # Names not predicted
    test_results = forecast_all_users(dat, prediction_dt=testing_date, test_metrics=True, print_loading=True)
    pred_results = forecast_all_users(dat, prediction_dt=prediction_date, test_metrics=False)

    final_results = pd.merge(test_results, pred_results, on='Name', how='outer')
    filename = 'csm_fixed_predictions_{}.csv'.format(reformatDateString(testing_date, '%Y_%m'))
    str_csv = final_results.to_csv(filename, index=False)  # CSV file

    # Email csv file with metrics
    prediction_month_name = reformatDateString(prediction_date, '%b %Y')
    testing_month_name = reformatDateString(testing_date, '%b %Y')
    MAE = round(np.nanmean(abs(final_results[['Error']])), 2)
    MedAE = round(np.nanmedian(abs(final_results[['Error']])),2)
    MedAPE = 100 * round(np.nanmedian(abs(final_results[['Percent Error']])), 4)

    msg = MIMEMultipart()
    msg['From'] = 'thisisatestingemail497@gmail.com'
    msg['To'] = 'TO_EMIAL_ADDRESS'
    msg['Subject'] = 'CSM predictions {}'.format(testing_month_name)
    message = MIMEText(
        """CSM accuracy testing for {} and future predictions for {}

            Metrics
            Mean Absolute Error:       {}
            Median Absolute Error:    {}
            Median Absolute % Error: {}%
        """.format(testing_month_name, prediction_month_name, MAE, MedAE, MedAPE))
    msg.attach(message)

    part = MIMEApplication(str_csv, Name=basename(filename))

    # part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filename)
    msg.attach(part)

    gmail_sender = 'thisisatestingemail497@gmail.com'
    gmail_passwd = 'INSERT PASSCODE HERE'

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_sender, gmail_passwd)

    server.send_message(msg)
    server.quit()


