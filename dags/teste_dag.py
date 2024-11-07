from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

# Função de teste para o PythonOperator
def hello_world():
    print("Hello, Airflow!")

# Configuração básica do DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Criando o DAG
with DAG(
    dag_id='dag_teste',
    default_args=default_args,
    description='DAG de teste simples',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Operador Dummy para uma tarefa de início
    start = DummyOperator(
        task_id='start'
    )

    # Operador Python para executar a função hello_world
    hello_task = PythonOperator(
        task_id='hello_task',
        python_callable=hello_world,
    )

    # Operador Dummy para uma tarefa de fim
    end = DummyOperator(
        task_id='end'
    )

    # Definindo a ordem das tarefas
    start >> hello_task >> end
