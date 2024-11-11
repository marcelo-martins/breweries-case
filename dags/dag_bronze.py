from airflow import DAG
# from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.hooks.base_hook import BaseHook
import boto3
from airflow.operators.python_operator import PythonOperator
import requests
import pandas as pd
import io
from datetime import datetime, timedelta

def get_boto3_client():
    # Obtendo credenciais do Airflow
    connection = BaseHook.get_connection('awsconn')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=connection.login,
        aws_secret_access_key=connection.password,
        region_name='us-east-2'
    )
    return s3_client

# Função de teste para o PythonOperator
def fetch_brewery_data_to_s3():
    API_URL = 'https://api.openbrewerydb.org/breweries'
    
    # Fazendo a requisição para a API
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Usando boto3 para se conectar ao S3
        s3_client = get_boto3_client()
        bucket_name = 'abi-bees-case-2'
        s3_key = 'bronze/brewery_data.csv'
        
        # Enviando o arquivo CSV para o S3
        s3_client.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=s3_key)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definindo o DAG
dag = DAG(
    'fetch_brewery_data_to_s3',
    description='Busca dados de breweries da API e salva no S3',
    schedule_interval=None,  # Pode ser ajustado para rodar periodicamente
    start_date=datetime(2024, 11, 7),
    catchup=False,
)

# Definindo o operador Python para rodar a função
fetch_data_task = PythonOperator(
    task_id='fetch_brewery_data',
    python_callable=fetch_brewery_data_to_s3,
    dag=dag,
)

# Adicionando as dependências, neste caso é uma tarefa única
fetch_data_task
