# Usando a imagem base do Apache Airflow
FROM apache/airflow:2.6.1-python3.9

# Instalando o Java necessário para o PySpark
USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget

# Instalando o Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz && \
    mkdir -p /opt/spark && \
    tar -xzf spark-3.4.0-bin-hadoop3.tgz -C /opt/spark --strip-components=1 && \
    rm spark-3.4.0-bin-hadoop3.tgz

RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P /opt/spark/jars/ && \
wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.354/aws-java-sdk-bundle-1.12.354.jar -P /opt/spark/jars/

# Configurando o ambiente do Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

USER airflow

# Instalando o PySpark
RUN pip install pyspark