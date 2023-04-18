import os
import boto3
import pymysql
import requests

# Initialize S3 client
s3_client = boto3.client('s3')

#Connect to Database
endpoint = 'my-aeronautics-db.cb95ufq3bxca.us-east-1.rds.amazonaws.com'#os.environ['HOST']
username = 'admin'#os.environ['USER']
password = 'password'#os.environ['PASSWORD']
db_name = 'spaceBDD'#os.environ['NAME']


connection = pymysql.connect(host=endpoint, user=username,password=password, database=db_name)

# Lambda function handler
def lambda_handler(event, context):
    try:
        with connection.cursor() as cursor:
            # SQL query for rocket images
            sql = """SELECT DISTINCT name, image_url FROM 
                        rockets AS r
                        INNER JOIN rocket_images
                        ON r.id = rocket_images.rocket_id"""
            cursor.execute(sql)

            # Fetch the first batch of rows
            batch_size = 100
            rockets = cursor.fetchmany(batch_size)

            while rockets:
                # Loop through the batch of rows and download rocket images
                for row in rockets:
                    rocket_name = row['name']
                    image_url = row['image_url']
                    image_data = requests.get(image_url).content

                    # Upload the image to S3
                    s3_client.put_object(
                        Body=image_data,
                        Bucket='spacexetl-images',
                        Key=f'{rocket_name}/' + os.path.basename(image_url)
                    )

                    print('{} image downloaded and uploaded to S3:{}'.format(rocket_name, image_url))

                # Fetch the next batch of rows
                rockets = cursor.fetchmany(batch_size)

            sql = """SELECT DISTINCT name, image_url FROM 
                        rockets AS r
                        INNER JOIN launch_images
                        ON r.id = launch_images.rocket_id"""
            cursor.execute(sql)

            # Fetch the first batch of rows
            launches = cursor.fetchmany(batch_size)

            while launches:
                # Loop through the batch of rows and download launch images
                for row in launches:
                    rocket_name = row['name']
                    image_url = row['image_url']
                    image_data = requests.get(image_url).content

                    # Upload the image to S3
                    s3_client.put_object(
                        Body=image_data,
                        Bucket='spacexetl-images',
                        Key=f'{rocket_name}/' + os.path.basename(image_url)
                    )

                    print('{} launch image downloaded and uploaded to S3: {}'.format(rocket_name, image_url))

                # Fetch the next batch of rows
                launches = cursor.fetchmany(batch_size)

    except:
        print('Failed to download images')
    finally:
        connection.close()

