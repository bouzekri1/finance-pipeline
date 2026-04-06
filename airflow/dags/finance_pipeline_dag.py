from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import sys
import os
sys.path.insert(0, '/opt/airflow/ingestion')

#import des script de fetch api et chargement dans Redshift
import fetch_sirene
import load_many_to_redshift

#Déclaration du DAG
with DAG(
    dag_id="finance_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    # Tâche 1
    t1 = PythonOperator(
        task_id="fetch_sirene",
        python_callable=fetch_sirene.main
    )

    # Tâche 2
    t2 = PythonOperator(
        task_id="load_to_redshift",
        python_callable=load_many_to_redshift.main
    )

    # Tâche 3
    t3 = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run && dbt run"
    )

    # Ordre d'exécution
    t1 >> t2 >> t3