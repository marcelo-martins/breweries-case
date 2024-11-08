from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python_operator import PythonOperator
import requests
import pandas as pd
import io
from datetime import datetime, timedelta

# Função de teste para o PythonOperator
def fetch_brewery_data_to_s3():
    API_URL = 'https://api.openbrewerydb.org/breweries'
    
    # Fazendo a requisição para a API
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        # Convertendo a resposta para JSON
        data = response.json()
        
        # Convertendo para DataFrame
        df = pd.DataFrame(data)
        
        # Salvando em um buffer (em memória)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Conectando ao S3
        s3_hook = S3Hook(aws_conn_id='awsconn')
        
        # Nome do bucket e caminho no S3
        bucket_name = 'abi-bees-case-2'
        s3_key = 'bronze/brewery_data.csv'
        
        # Enviando o CSV para o S3
        s3_hook.load_string(csv_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)

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
