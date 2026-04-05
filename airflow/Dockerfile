FROM apache/airflow:2.8.1
USER root
RUN apt-get update && apt-get install -y git
USER airflow
RUN pip install dbt-core==1.8.1 dbt-redshift==1.8.1
