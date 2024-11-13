# Brewery API data to data lake
This repository was built to solve a data engineering problem: reading data from an API and creating a view with it.

The main idea is to develop a medallion architecture in a data lake (AWS S3 in this case) and creating the necessary files to achive the desired view.

## Tools

This project uses the following tools:
+ **Airflow**: used for orchestrating the ETL pipeline, scheduling and managing task execution, such as API calls and data transformations
+ **Docker**: provides containerization to ensure that the application and its dependencies run consistently across environments. It also manages the Airflow components and database
+ **Pandas** and **Pyspark**: used for business rules and data conversion

## Main files
1. **docker-compose.yml** - this file is responsible for creating the containers. There are three containers in this project:
    1. One for the airflow webserver
    2. One for the airflow scheduler
    3. One for the database (postgres) necessary to store the airflow data
2. **Dockerfile** - this file is used to create a custom docker image used in the airflow containers
    This image is based on the official airflow image (**apache/airflow:tag**), but with spark installed
    The file follows a straightforward configuration that runs `wget` to get spark and configures the necessary jars and environment variables, such as **SPARK_HOME**, **JAVA_HOME** and the .jars for AWS S3 support
3. **utils** folder
    This folder contains helper functions developed to instanciate the SparkSession and writing to S3
4. **plugins** folder
    This folder contains the **dags_logic.py** file, which has all the business rules of the dags, including the API request, data conversion and write to the layers in the lake
5. **requirements.txt**
    File that has all the python dependencies
6. **.envexample**
    This file must be renamed to ".env" and its values must be changed to your AWS S3 credentials. Please refer to [How to create aws access key](https://joegalley.com/articles/how-to-create-aws-access-key-and-secret-access-key)

## Installation
If you are interested in running this application on your local machine, here are the necessary steps:
1. Installing Docker e Docker Compose on [Windows](https://docs.docker.com/desktop/setup/install/windows-install/), [Linux](https://docs.docker.com/desktop/setup/install/linux/) or [Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
2. If on Windows, open the Docker Desktop Application
3. Clone this repository and cd into it. `cd path/to/repo`
4. Run `docker-compose up --build -d`. The build flag is only necessary if you change anything in the code. The `-d` flag allows you to keep using the same terminal and it is also optional.
5. Access **http://localhost:8080/** to interact with the Airflow UI. You can run the DAG from there

## How the code works
After running the DAG, the follow steps are executed:
+ A call to the **https://api.openbrewerydb.org/breweries** is made. The result is stored in a pandas dataframe as a csv and then uploaded to S3 in the bronze layer
+ If the above step runs successfully, the next DAG reads the data from the bronze layer with PySpark, converts it to parquet, partitions the file by type and location (`brewery_type`, `country`, `state_province` and `city`), drops the `state` column, as it is the same as `state_province` and finally, writes it to the silver layer
+ If the above step also runs successfully, the next DAG reads the data from the silver layer with PySpark, aggregates it to create a simple view with the amount of breweries by type and location and writes it to the gold layer
+ If you leave the airflow webserver running, the DAG will reprocess daily

## Design choices
+ This project creates a simple data lake structure by splitting a bucket in three folders: bronze, silver and gold, even though AWS recommends to create [one bucket to each layer](https://docs.aws.amazon.com/prescriptive-guidance/latest/defining-bucket-names-data-lakes/data-layer-definitions.html) for security purposes
+ To share environment variables between the conteiner and the DAGS, the **docker-compose** file read the **.env** file and creates airflow variables that can be used by any DAG. This approach is probably not the most efficient to be used in production
+ The airflow, pyspark and .jars versions are defined in the Dockerfile but this code should work in most recent versions as well, but this has **not** been tested

## Monitoring