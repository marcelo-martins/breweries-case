FROM apache/airflow:2.5.3-python3.8

# Install Java
USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget

# Install Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz && \
    mkdir -p /opt/spark && \
    tar -xzf spark-3.3.2-bin-hadoop3.tgz -C /opt/spark --strip-components=1 && \
    rm spark-3.3.2-bin-hadoop3.tgz

# Configuring Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Downloading the aws jars
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar -P "${SPARK_HOME}/jars/" && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -P "${SPARK_HOME}/jars/"

USER airflow

# Install PySpark
RUN pip install pyspark
