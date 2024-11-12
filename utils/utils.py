from airflow.hooks.base_hook import BaseHook
import boto3
from pyspark.sql import SparkSession

def get_boto3_client():
    connection = BaseHook.get_connection('awsconn')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=connection.login,
        aws_secret_access_key=connection.password,
        region_name='us-east-2'
    )
    return s3_client, connection

def get_spark_session():
    _, connection = get_boto3_client()

    return SparkSession.builder \
    .appName("BreweryDataProcessing") \
    .config("spark.executor.instances", "10") \
    .config("spark.executor.cores", "2") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.access.key", connection.login) \
    .config("spark.hadoop.fs.s3a.secret.key", connection.password) \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.region", "us-east-2") \
    .getOrCreate()