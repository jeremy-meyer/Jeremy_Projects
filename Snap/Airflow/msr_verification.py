from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'dashboard',
    'depends_on_past': False,
    'start_date': datetime(2019, 8, 13, 00, 00),
    'email': ['EMAIL_ADDRESS'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'backfill': False,
    'sla': timedelta(hours=1),
    'execution_timeout': timedelta(hours=0, minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    'max_active_runs': 1,
}

dag = DAG(
    'msr_verification_code',
    default_args=default_args,
    schedule_interval="0 9 * * *",
    catchup=False)

CallDataLatest = DockerOperator(
    task_id='msr_verification_code',
    image='DOCKER IMAGE',
    command="Rscript MSR_verification_code.R",
    dag=dag,
    force_pull=True
)