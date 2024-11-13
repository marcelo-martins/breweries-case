import requests
import pandas as pd
import sys
sys.path.append('/opt/airflow/utils')
import utils
from pyspark.sql import functions as F
from airflow.models import Variable
import logging

logger = logging.getLogger(__name__)

BRONZE_KEY = 'bronze/brewery_data.csv'
SILVER_KEY = 'silver'
GOLD_KEY = 'gold'
API_URL = 'https://api.openbrewerydb.org/breweries'
AWS_BUCKET_NAME = Variable.get("AWS_BUCKET_NAME")

def bronze_fetch_brewery_data_to_s3():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception(f'Error fetching data from the API. Status code {response.status_code}')
        raise Exception(f'Error fetching data from the API. Status code {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        try:
            df.to_csv(f"s3a://{AWS_BUCKET_NAME}/{BRONZE_KEY}", index=False, storage_options={
                'key': Variable.get("AWS_ACCESS_KEY"),
                'secret': Variable.get("AWS_SECRET_KEY")
            })
        except Exception as e:
            logger.exception(f'Error writing data to the bronze layer in AWS S3')
            raise
        
def silver_process_data_to_parquet(): 
    s3_bronze_path = f"s3a://{AWS_BUCKET_NAME}/{BRONZE_KEY}"
    s3_silver_path = f"s3a://{AWS_BUCKET_NAME}/{SILVER_KEY}"

    try:
        spark = utils.get_spark_session()
    except Exception as e:
        logger.exception(f'Error during SparkSession creation')
        raise

    try:
        df_bronze = spark.read.csv(s3_bronze_path, header=True).drop('state')
    except Exception as e:
        logger.exception(f'Error fetching data from bronze layer in AWS S3')
        raise

    try:
        utils.s3_write_parquet(df=df_bronze, path=s3_silver_path, partition_columns=["brewery_type", "country", "state_province", "city"])
    except Exception as e:
        logger.exception(f'Error writing data to silver layer in AWS S3')
        raise
    
def gold_create_view_lake():
    s3_silver_path = f"s3a://{AWS_BUCKET_NAME}/{SILVER_KEY}"
    s3_gold_path = f"s3a://{AWS_BUCKET_NAME}/{GOLD_KEY}"

    try:
        spark = utils.get_spark_session()
    except Exception as e:
        logger.exception(f'Error during SparkSession creation')
        raise

    try:
        df_silver = spark.read.parquet(s3_silver_path)
    except Exception as e:
        logger.exception(f'Error fetching data from bronze layer in AWS S3')
        raise
    
    df_gold = df_silver.groupBy("brewery_type", "country", "state_province", "city").agg(F.count('*').alias('count_breweries'))
    
    try:
        utils.s3_write_parquet(df=df_gold, path=s3_gold_path)
    except Exception as e:
        logger.exception(f'Error writing view to gold layer in AWS S3')
        raise