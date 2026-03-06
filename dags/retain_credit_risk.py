from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner':            'ml-team',
    'depends_on_past':  False,
    'retries':          2,
    'retry_delay':      timedelta(minutes=10),
    'email_on_failure': True,
    'email':            ['you@example.com'],
}

def check_for_drift(**context):
    import sys; sys.path.insert(0, '.')
    from src.monitoring.drift_detection import run_drift_report
    result = run_drift_report(
        'data/processed/reference.csv',
        'data/processed/current.csv'
    )
    context['ti'].xcom_push(key='drift_result', value=result)
    return 'retrain_model' if result['drift_detected'] else 'skip_retraining'

def retrain_model(**context):
    logger.info('Starting model retraining...')
    # Calls your training script

def skip_retraining(**context):
    logger.info('No drift detected. Skipping retraining.')

with DAG(
    dag_id='credit_risk_monitoring_retrain',
    default_args=default_args,
    schedule_interval='0 6 * * MON',  # Every Monday at 6am
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['credit-risk', 'ml', 'monitoring']
) as dag:

    validate_data  = PythonOperator(task_id='validate_data',  python_callable=lambda: None)
    drift_check    = BranchPythonOperator(task_id='drift_check', python_callable=check_for_drift)
    retrain        = PythonOperator(task_id='retrain_model',   python_callable=retrain_model)
    skip           = PythonOperator(task_id='skip_retraining', python_callable=skip_retraining)
    notify         = BashOperator(task_id='send_report', bash_command='echo Retraining complete')
