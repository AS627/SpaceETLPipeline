from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from landpad import extract, validate, transform, load

default_args = {
    'owner': 'Amogh Srigopal',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag_landpad = DAG(
    dag_id ='landpad',
    default_args=default_args,
    description='DAG for fetching launchpad and landpad data',
    schedule=timedelta(minutes=5)
)

extract_landpads = PythonOperator(
    task_id='extract_landpads',
    python_callable=extract, 
    dag=dag_landpad
)

validate_landpads = PythonOperator(
    task_id='validate_landpads',
    python_callable=validate, 
    op_args=[extract_landpads.output],
    dag=dag_landpad
)

transform_landpads = PythonOperator(
    task_id='transform_landpads',
    python_callable=transform, 
    op_args=[validate_landpads.output],
    dag=dag_landpad
)

load_landpads = PythonOperator(
    task_id='load_landpads',
    python_callable=load, 
    op_args=[transform_landpads.output],
    dag=dag_landpad
)

