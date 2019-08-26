from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'dashboard',
    'depends_on_past': False,
    'start_date': datetime(2019, 8, 16, 00, 00),
    'email': ['email_address'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'backfill': False,
    'sla': timedelta(hours=1),
    'execution_timeout': timedelta(hours=1, minutes=0),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    'max_active_runs': 1,
}

dag = DAG(
    'collections_gen_predictions',
    default_args=default_args,
    schedule_interval="30 14 1,3 * *", # 8am 1st/3rd day of month
    catchup=False)

CallDataLatest = DockerOperator(
    task_id='collections_gen_predictions',
    image='DOCKER IMAGE',
    command="python3 collections_forecast_preds.py",
    dag=dag,
    force_pull=True
)