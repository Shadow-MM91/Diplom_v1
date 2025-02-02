from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow import DAG

from datetime import datetime
from tasks.etl.test_data.test_data_gener import test_data_gener
from tasks.etl.query_sql import create_test_tables

default_args = {
}

with DAG(
        dag_id='load_gener_data',
        start_date=datetime(2025, 1, 25),
        schedule_interval='*/1 * * * *',
        default_args=default_args,
        catchup=False,
) as dag:

    create_task = SQLExecuteQueryOperator(
        task_id='create_tables',
        conn_id='DB_connect',
        sql=create_test_tables,
    )

    stg_load_task = PythonOperator(
        task_id='stg-load',
        python_callable=test_data_gener,
        op_kwargs={"hook": PostgresHook(postgres_conn_id='DB_connect')},
    )

create_task >> stg_load_task