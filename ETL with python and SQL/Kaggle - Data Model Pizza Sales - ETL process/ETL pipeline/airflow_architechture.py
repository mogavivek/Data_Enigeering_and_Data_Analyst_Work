# ========================== airflow_pipeline.py ==========================

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pipeline.pipeline import StatistaPipeline

# Pipeline function
def run_pipeline():
    pipeline = StatistaPipeline()
    pipeline.run()
    
# Default DAG settings
default_args = {
    "owner": "name_any",
    "depends_on_past": False,
    "email": ["WriteYourEmail@email.com"], # Send alert email
    "email_on_failure": True, # Email if pipeline fails
    "email_on_retry": False,
    "retries": 2, # Retry failed jobs
    "retry_delay": timedelta(minutes=5)
}

# DAG definition
with DAG(
    dag_id="statista_daily_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily", # Run every day
    catchup=False
) as dag:

    run_etl = PythonOperator(
        task_id="run_statista_pipeline",
        python_callable=run_pipeline
    )
    run_etl