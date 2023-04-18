##SPACE ETL PIPELINE
This is an ETL pipeline that fetches rocket and launch mission data from SpaceX REST API, and saves that data in Amazon RDS. 
This pipeline is orchestrated through Apache Airflow running on Docker. 
The data users then apply further image processing and data visualization methods. 

#Setting up Airflow with Docker:

Followed Documentation provided in

https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html 

Setup and Cleanup Commands
docker compose up airflow-init 
docker compose up -d 
docker-compose down -v 
