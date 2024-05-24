import os
import boto3
import pymysql
import requests

# Initialize the AWS S3 client
s3_client = boto3.client('s3')

# Database configuration
db_host = os.environ['DB_HOST']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

# Lambda function handler
def lambda_handler(event, context):
    # Connect to the MySQL database
    db_conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        db=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with db_conn.cursor() as cursor:
            # Execute SQL queries on the database
            sql = "SELECT image_url FROM images"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            # Loop through the query result and download images
            for row in result:
                image_url = row['image_url']
                image_data = requests.get(image_url).content
                
                # Upload the image to S3
                s3_client.put_object(
                    Body=image_data,
                    Bucket='your-s3-bucket-name',
                    Key='images/' + os.path.basename(image_url)
                )
                
                print('Image downloaded and uploaded to S3:', image_url)
            
    finally:
        # Close the database connection
        db_conn.close()