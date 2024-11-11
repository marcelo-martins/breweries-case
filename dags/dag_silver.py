# from airflow import DAG
# # from airflow.providers.amazon.aws.hooks.s3 import S3Hook
# from airflow.hooks.base_hook import BaseHook
# import boto3
# from airflow.operators.python_operator import PythonOperator
# import requests
# import pandas as pd
# import io
# from datetime import datetime, timedelta
# from pyspark.sql import SparkSession

# def get_boto3_client():
#     # Obtendo credenciais do Airflow
#     connection = BaseHook.get_connection('awsconn')
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=connection.login,
#         aws_secret_access_key=connection.password,
#         region_name='us-east-2'
#     )
#     return s3_client

# # Função de teste para o PythonOperator
# def convert_data_to_parquet():
#     API_URL = 'https://api.openbrewerydb.org/breweries'

#     spark = SparkSession.builder \
#     .appName("MyAirflowDAG") \
#     .master("local[*]") \
#     .getOrCreate()
    
#     # Fazendo a requisição para a API
#     response = requests.get(API_URL)
    
#     if response.status_code == 200:
#         data = [
#             (1, "BrewDog", "Columbus", "Ohio"),
#             (2, "Stone Brewing", "Escondido", "California"),
#             (3, "Lagunitas Brewing Company", "Petaluma", "California"),
#             (4, "Sierra Nevada", "Chico", "California"),
#             (5, "Ballast Point", "San Diego", "California")
#         ]
#         columns = ["brewery_id", "name", "city", "state"]
#         df = spark.createDataFrame(data, columns)
#         print(df.show())
#         df = df.toPandas()

#         csv_buffer = io.StringIO()
#         df.to_csv(csv_buffer, index=False)
#         csv_buffer.seek(0)
        
#         # Usando boto3 para se conectar ao S3
#         s3_client = get_boto3_client()
#         bucket_name = 'abi-bees-case-2'
#         s3_key = 'bronze/brewery_data.csv'
        
#         # Enviando o arquivo CSV para o S3
#         s3_client.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=s3_key)

# default_args = {
#     'owner': 'airflow',
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# # Definindo o DAG
# dag = DAG(
#     'convert_data_to_parquet',
#     description='Busca dados de breweries da API e salva no S3',
#     schedule_interval=None,  # Pode ser ajustado para rodar periodicamente
#     start_date=datetime(2024, 11, 7),
#     catchup=False,
# )

# # Definindo o operador Python para rodar a função
# teste = PythonOperator(
#     task_id='convert',
#     python_callable=convert_data_to_parquet,
#     dag=dag,
# )

# # Adicionando as dependências, neste caso é uma tarefa única
# teste


from airflow import DAG
# from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.hooks.base_hook import BaseHook
import boto3
from airflow.operators.python_operator import PythonOperator
import requests
import pandas as pd
import io
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
#from pyspark.sql import functions as F

def get_boto3_client():
    # Obtendo credenciais do Airflow
    connection = BaseHook.get_connection('awsconn')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=connection.login,
        aws_secret_access_key=connection.password,
        region_name='us-east-2'
    )
    return s3_client, connection

# Função de teste para o PythonOperator
def process_data_to_parquet():
    
    s3_client, connection = get_boto3_client()
    bucket_name = 'abi-bees-case-2'
    bronze_key = 'bronze/brewery_data.csv'
    silver_key = 'silver/brewery_data.parquet'

    # Recupera o arquivo da Bronze
    response = s3_client.get_object(Bucket=bucket_name, Key=bronze_key)
    csv_data = response['Body'].read().decode('utf-8')

    # Converte para DataFrame e Parquet
    pdf = pd.read_csv(io.StringIO(csv_data))
    print(f'DF DO PANDA {pdf.head()}')
    spark = SparkSession.builder \
    .appName("BreweryDataProcessing") \
    .config("spark.hadoop.fs.s3.access.key", connection.login) \
    .config("spark.hadoop.fs.s3.secret.key", connection.password) \
    .config("spark.hadoop.fs.s3.endpoint", "s3.amazonaws.com") \
    .config("spark.hadoop.fs.s3.region", "us-east-2") \
    .getOrCreate()
    df = spark.createDataFrame(pdf)
    # print(f'DF DO SPARK {df.show()}')
    df.write.mode("overwrite").partitionBy("brewery_type", "state_province", "city").parquet(f"s3://{bucket_name}/{silver_key}")

    # # Salva na camada Silver
    # parquet_buffer.seek(0)
    # s3_client.put_object(Body=parquet_buffer.getvalue(), Bucket=bucket_name, Key=silver_key)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definindo o DAG
dag = DAG(
    'process_data_to_parquet',
    description='Busca dados de breweries da API e salva no S3',
    schedule_interval=None,  # Pode ser ajustado para rodar periodicamente
    start_date=datetime(2024, 11, 7),
    catchup=False,
)

# Definindo o operador Python para rodar a função
convert_data_task = PythonOperator(
    task_id='convert_brewery_data',
    python_callable=process_data_to_parquet,
    dag=dag,
)

# Adicionando as dependências, neste caso é uma tarefa única
convert_data_task
