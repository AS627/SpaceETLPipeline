from airflow.models import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


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
fetch_rockets = BashOperator(
    task_id='rocket',
    bash_command=' python rockets.py', 
    dag=dag_rocket
)

#Launch Task
fetch_launches = BashOperator(
    task_id='launch',
    bash_command='python launches.py', 
    dag=dag_launch
)

#Launchpad Task
fetch_launchpads = BashOperator(
    task_id='launchpad',
    bash_command='python launchpad.py', 
    dag=dag_pads,
)

#Landpad Task
fetch_landpads = BashOperator(
    task_id='landpad',
    bash_command='python landpad.py', 
    dag=dag_pads
)

