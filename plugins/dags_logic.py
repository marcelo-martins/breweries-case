import requests
import pandas as pd
import io
import sys
sys.path.append('/opt/airflow/utils')
import utils
from pyspark.sql import functions as F

def fetch_brewery_data_to_s3():
    API_URL = 'https://api.openbrewerydb.org/breweries'
    
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        s3_client, _ = utils.get_boto3_client()
        bucket_name = 'abi-bees-case-2'
        s3_key = 'bronze/brewery_data.csv'
        
        s3_client.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=s3_key)

def process_data_to_parquet(): 
    bucket_name = 'abi-bees-case-2'
    bronze_key = 'bronze/brewery_data.csv'
    silver_key = 'silver'

    spark = utils.get_spark_session()

    df_bronze = spark.read.csv(f"s3a://{bucket_name}/{bronze_key}", header=True).drop('state')

    df_bronze.write.mode("overwrite"). \
        option("compression", "SNAPPY"). \
        partitionBy("brewery_type", "country", "state_province", "city"). \
        parquet(f"s3a://{bucket_name}/{silver_key}")
    
def create_view_lake():
    bucket_name = 'abi-bees-case-2'
    silver_key = 'silver'
    gold_key = 'gold'

    spark = utils.get_spark_session()

    df_silver = spark.read.parquet(f"s3a://{bucket_name}/{silver_key}")
    
    df_gold = df_silver.groupBy("brewery_type", "country", "state_province", "city").agg(F.count('*').alias('count_breweries'))
    
    df_gold.write.mode("overwrite").parquet(f"s3a://{bucket_name}/{gold_key}")