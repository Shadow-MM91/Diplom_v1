from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow import DAG

from datetime import datetime, timedelta
from tasks.etl.etl_nds_def import nds
from tasks.etl.query_sql import (generate_schema,
                                 create_test_tables,
                                 generate_tables_dds,
                                 update_dds_tables,
                                 update_dds_fact)

default_args = {
}

with DAG(
        dag_id='etl_processing',
        start_date=datetime(2025, 1, 25),
        schedule_interval='*/2 * * * *',
        default_args=default_args,
        catchup=False,
) as dag:

    start = EmptyOperator(task_id='start')

    schema_create_task = SQLExecuteQueryOperator(
        task_id='schema_create',
        conn_id='DB_connect',
        sql=generate_schema,
    )

    test_table_create_task = SQLExecuteQueryOperator(
        task_id='test_table_create',
        conn_id='DB_connect',
        sql=create_test_tables,
    )

    nds_load_task = PythonOperator(
        task_id='nds-load',
        python_callable=nds,
        op_kwargs={"hook": PostgresHook(postgres_conn_id='DB_connect')},
    )

    dds_create_task = SQLExecuteQueryOperator(
        task_id='dds-create',
        conn_id='DB_connect',
        sql=generate_tables_dds,
    )

    dds_dim_load_task = SQLExecuteQueryOperator(
        task_id='dds-meas-load',
        conn_id='DB_connect',
        sql=update_dds_tables,
    )

    dds_fact_load_task = SQLExecuteQueryOperator(
        task_id='dds-fact-load',
        conn_id='DB_connect',
        sql=update_dds_fact,
    )

start >> [schema_create_task, test_table_create_task] >> nds_load_task >> dds_create_task >> dds_dim_load_task >> dds_fact_load_task