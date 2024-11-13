from pyspark.sql import SparkSession
from airflow.models import Variable

def get_spark_session():
    return SparkSession.builder \
    .appName("BreweryDataProcessing") \
    .config("spark.executor.instances", "10") \
    .config("spark.executor.cores", "2") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.access.key", Variable.get("AWS_ACCESS_KEY")) \
    .config("spark.hadoop.fs.s3a.secret.key", Variable.get("AWS_SECRET_KEY")) \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.region", "us-east-2") \
    .getOrCreate()

def s3_write_parquet(df, path, partition_columns=None, mode="overwrite"):
    if partition_columns:
        if not isinstance(partition_columns, list):
            partition_columns = [partition_columns]

        df.write.mode(mode) \
            .option("compression", "SNAPPY") \
            .partitionBy(partition_columns) \
            .parquet(path)
    else:
        df.write.mode(mode) \
            .option("compression", "SNAPPY") \
            .parquet(path)