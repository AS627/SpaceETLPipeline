from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from rockets import extract_images, extract_rockets
from rockets import transform_image, transform_rocket
from rockets import valid_image, valid_rocket, load
from rockets import rocket_query, image_query

default_args = {
    'owner': 'Amogh Srigopal',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag_rocket = DAG(
    dag_id='rockets',
    default_args=default_args,
    description='DAG for fetching rocket data',
    schedule=timedelta(days=1),  
)

extract_rocket = PythonOperator(
    task_id='extract_rockets',
    python_callable=extract_rockets, 
    dag=dag_rocket
)

extract_image = PythonOperator(
    task_id='rocket_images',
    python_callable=extract_images, 
    dag=dag_rocket
)

validate_rocket = PythonOperator(
    task_id='validate_rockets',
    python_callable=valid_rocket, 
    op_args=[extract_rocket.output],
    dag=dag_rocket
)

validate_image = PythonOperator(
    task_id='validate_rimages',
    python_callable=valid_image, 
    op_args=[extract_image.output],
    dag=dag_rocket
)

transform_rockets = PythonOperator(
    task_id='transform_rockets',
    python_callable=transform_rocket, 
    op_args=[validate_rocket.output],
    dag=dag_rocket
)

transform_images = PythonOperator(
    task_id='transform_rimages',
    python_callable=transform_image, 
    op_args=[validate_image.output],
    dag=dag_rocket
)

load_rockets = PythonOperator(
    task_id='load_rockets',
    python_callable=load,
    op_args=[transform_rockets.output, rocket_query], 
    dag=dag_rocket
)

load_image = PythonOperator(
    task_id='load_rimages',
    python_callable=load,
    op_args=[transform_images.output, image_query], 
    dag=dag_rocket
)

