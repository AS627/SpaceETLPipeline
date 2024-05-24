from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from launchpad import extract, validate, transform, load

default_args = {
    'owner': 'Amogh Srigopal',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag_launchpad = DAG(
    dag_id ='launchpad',
    default_args=default_args,
    description='DAG for fetching launchpad and landpad data',
    schedule=timedelta(minutes=5)
)

extract_launchpads = PythonOperator(
    task_id='extract_launchpads',
    python_callable=extract, 
    dag=dag_launchpad
)

validate_launchpads = PythonOperator(
    task_id='validate_launchpads',
    python_callable=validate, 
    op_args=[extract_launchpads.output],
    dag=dag_launchpad
)

transform_launchpads = PythonOperator(
    task_id='transform_launchpads',
    python_callable=transform, 
    op_args=[validate_launchpads.output],
    dag=dag_launchpad
)

load_launchpads = PythonOperator(
    task_id='load_launchpads',
    python_callable=load, 
    op_args = [transform_launchpads.output],
    dag=dag_launchpad
)

