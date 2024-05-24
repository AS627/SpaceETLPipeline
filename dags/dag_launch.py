from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from launches import extract_images, extract_launches
from launches import transform_launch, transform_image
from launches import valid_image, valid_launch, load 
from launches import launch_query, image_query

default_args = {
    'owner': 'Amogh Srigopal',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag_launch = DAG(
    dag_id='launches',
    default_args=default_args,
    description='DAG for fetching launch data',
    schedule=timedelta(seconds=20), 
)

extract_launch = PythonOperator(
    task_id='extract_launches',
    python_callable=extract_launches, 
    dag=dag_launch
)

extract_image = PythonOperator(
    task_id='launch_images',
    python_callable=extract_images,
    dag=dag_launch
)

validate_launch = PythonOperator(
    task_id='validate_launches',
    python_callable=valid_launch, 
    op_args=[extract_launch.output],
    dag=dag_launch
)

validate_image = PythonOperator(
    task_id='validate_limages',
    python_callable=valid_image, 
    op_args=[extract_image.output],
    dag=dag_launch
)

transform_launches = PythonOperator(
    task_id='transform_launches',
    python_callable=transform_launch, 
    op_args=[validate_launch.output],
    dag=dag_launch
)

transform_images = PythonOperator(
    task_id='transform_limages',
    python_callable=transform_image, 
    op_args=[validate_image.output],
    dag=dag_launch
)

load_launch = PythonOperator(
    task_id='load_launches',
    python_callable=load,
    op_args=[transform_launches.output, launch_query], 
    dag=dag_launch
)

load_image = PythonOperator(
    task_id='load_limages',
    python_callable=load, 
    op_args=[transform_images.output, image_query], 
    dag=dag_launch
)
