# # Usando a imagem base do Apache Airflow
# FROM apache/airflow:2.6.1-python3.9

# # Instalando o Java necessário para o PySpark
# USER root
# RUN apt-get update && \
#     apt-get install -y openjdk-11-jdk wget

# # Instalando o Spark
# RUN wget -q https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz && \
#     mkdir -p /opt/spark && \
#     tar -xzf spark-3.4.0-bin-hadoop3.tgz -C /opt/spark --strip-components=1 && \
#     rm spark-3.4.0-bin-hadoop3.tgz


# # Configurando o ambiente do Spark
# ENV SPARK_HOME=/opt/spark
# ENV PATH=$SPARK_HOME/bin:$PATH
# ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P "${SPARK_HOME}/jars/" && \
#     wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/2.25.1/aws-java-sdk-bundle-2.25.11.jar -P "${SPARK_HOME}/jars/"

# USER airflow

# # Instalando o PySpark
# RUN pip install pyspark

# Usando uma imagem base do Apache Airflow com versão Python 3.8
FROM apache/airflow:2.5.3-python3.8

# Instalando o Java necessário para o PySpark
USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget

# Instalando o Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz && \
    mkdir -p /opt/spark && \
    tar -xzf spark-3.3.2-bin-hadoop3.tgz -C /opt/spark --strip-components=1 && \
    rm spark-3.3.2-bin-hadoop3.tgz

# Configurando o ambiente do Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Baixando as versões compatíveis das bibliotecas hadoop-aws e aws-java-sdk-bundle
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar -P "${SPARK_HOME}/jars/" && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -P "${SPARK_HOME}/jars/"

USER airflow

# Instalando o PySpark
RUN pip install pyspark
