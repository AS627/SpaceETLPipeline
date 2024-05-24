from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from rockets import rocket_etl
from launches import launch_etl
from launchpad import launchpad_etl
from landpad import landpad_etl


#Airflow Orchestration
default_args = {
    'owner': 'Amogh Srigopal',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Rocket DAG
dag_rocket = DAG(
    dag_id='rockets',
    default_args=default_args,
    description='DAG for fetching rocket data',
    schedule=timedelta(days=1),  
)

# Launch DAG
dag_launch = DAG(
    dag_id='launches',
    default_args=default_args,
    description='DAG for fetching launch data',
    schedule=timedelta(seconds=20), 
)

# Launchpad and Landpad DAG
dag_pads = DAG(
    dag_id ='pads',
    default_args=default_args,
    description='DAG for fetching launchpad and landpad data',
    schedule=timedelta(minutes=5)
)

#Rocket Task
rockets = PythonOperator(
    task_id='rocket',
    python_callable= rocket_etl, 
    dag=dag_rocket
)

#Launch Task
launches = PythonOperator(
    task_id='launch',
    python_callable=launch_etl, 
    dag=dag_launch
)

#Launchpad Task
launchpads = PythonOperator(
    task_id='launchpad',
    python_callable=launchpad_etl, 
    dag=dag_pads,
)

#Landpad Task
landpads = PythonOperator(
    task_id='landpad',
    python_callable=landpad_etl, 
    dag=dag_pads
)

rockets 
launches
launchpads
landpads