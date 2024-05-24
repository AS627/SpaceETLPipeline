from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pads import extract, validate, transform, load

default_args = {
    'owner': 'Amogh Srigopal',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag_pads = DAG(
    dag_id='pads',
    default_args=default_args,
    description='DAG for fetching launchpad and landpad data',
    schedule_interval=timedelta(minutes=5)
)

extract_landpads = PythonOperator(
    task_id='extract_landpads',
    python_callable=extract,
    op_args=['landpad'],
    dag=dag_pads
)

extract_launchpads = PythonOperator(
    task_id='extract_launchpads',
    python_callable=extract,
    op_args=['launchpad'],
    dag=dag_pads
)

validate_pads = PythonOperator(
    task_id='validate_pads',
    python_callable=validate, 
    op_args=[extract_landpads.output, extract_launchpads.output],
    dag=dag_pads
)

transform_pads = PythonOperator(
    task_id='transform_pads',
    python_callable=transform, 
    op_args=[validate_pads.output],
    dag=dag_pads
)

load_pads = PythonOperator(
    task_id='load_pads',
    python_callable=load, 
    op_args=[transform_pads.output],
    dag=dag_pads
)

extract_landpads >> extract_launchpads >> validate_pads >> transform_pads >> load_pads
