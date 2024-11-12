from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/utils')
import utils
sys.path.append('/opt/airflow/plugins')
import dags_logic

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'start_date': datetime(2024, 11, 7),
    'catchup': False,
}

with DAG(
    'generate_views_s3',
    description='DAG that executes all the necessary logic to update the lake (bronze, silver) and create the view (gold)',
    schedule_interval='@daily',
    default_args=default_args,
) as dag:

    fetch_data_task = PythonOperator(
        task_id='fetch_brewery_data',
        python_callable=dags_logic.fetch_brewery_data_to_s3,
    )

    convert_data_task = PythonOperator(
        task_id='convert_brewery_data',
        python_callable=dags_logic.process_data_to_parquet,
    )

    final_data_task = PythonOperator(
        task_id='create_views',
        python_callable=dags_logic.create_view_lake,
    )

fetch_data_task >> convert_data_task >> final_data_task
