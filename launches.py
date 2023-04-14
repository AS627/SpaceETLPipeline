import sqlalchemy
import pandas as pd 
import requests
import json
from sqlalchemy import text
from datetime import datetime

HOST = "my-aeronautics-db.cb95ufq3bxca.us-east-1.rds.amazonaws.com"
USER = 'admin'
PASS = 'password'
DB = 'spaceBDD'

#Data Validation 
def check_if_valid_launch(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new launches. Finishing execution")
		return False 
	# Primary Key Check
	if pd.Series(df['id']).is_unique:
		pass
	else:
		raise Exception("Invalid primary key")

	# Check for nulls
	if df[['id', 'launch_name', 'rocket_id', 'launch_date']].isnull().values.any():
		raise Exception("Null values found")
	return True

def check_if_valid_image(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new images. Finishing execution")
		return False 

	# Composite Primary Key Check
	temp = df[['id', 'launch_id']].value_counts(ascending=True).reset_index(name='count')
	for item in pd.Series(temp['count']):
		if item != 1:
			raise Exception("Invalid primary key")
	return True

r = requests.get('https://api.spacexdata.com/v4/launches')
data = r.json() 

ids = []
names = []
rocket_ids = []
success = []
dates = []



launch_ids = []
image_urls = []
fk_rocket_ids = []
image_increments = []

for i in range(len(data)):
	curr = data[i]
	for j in range(len(curr['links']['flickr']['original'])):
		image_increments.append(j)
		launch_ids.append(curr['id'])
		image_urls.append(curr['links']['flickr']['original'][j])
		fk_rocket_ids.append(curr['rocket'])
	ids.append(curr['id'])
	names.append(curr['name'])
	rocket_ids.append(curr['rocket'])
	success.append(curr['success'])
	dates.append(curr['date_unix'])

launch_dict = {
	'id': ids,
	'launch_name':names,
	'rocket_id': rocket_ids,
	'success': success,
	'launch_date': dates
}

images_dict = {
	'id': image_increments,
	'launch_id': launch_ids,
	'rocket_id': fk_rocket_ids,
	'image_url': image_urls
}

df_launches = pd.DataFrame(launch_dict, columns=['id', 'launch_name', 'rocket_id','success', 'launch_date'])

df_launch_images = pd.DataFrame(images_dict, columns=['id', 'launch_id', 'rocket_id', 'image_url'])

if check_if_valid_launch(df_launches):
    print("Data valid, proceed to Data Transformations")

if check_if_valid_image(df_launch_images):
    print("Data valid, proceed to Data Transformations")

#Data Tranformations

ts = [int(x) for x in df_launches['launch_date']]
df_launches['launch_date'] = [datetime.utcfromtimestamp(t).strftime('%Y-%m-%d') for t in ts]

df_launches['launch_date'] = pd.to_datetime(df_launches['launch_date'])


df_launches['id'] = df_launches['id'].astype(str)
df_launches['rocket_id'] = df_launches['rocket_id'].astype(str)
df_launches['launch_name'] = df_launches['launch_name'].astype(str)
df_launches['success'] = df_launches['success'].astype(bool)

df_launch_images['launch_id'] = df_launch_images['launch_id'].astype(str)
df_launch_images['rocket_id'] = df_launch_images['rocket_id'].astype(str)
df_launch_images['image_url'] = df_launch_images['image_url'].astype(str)

#Loading Stage
db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

engine = sqlalchemy.create_engine(db_url)

first_query = """
   CREATE TABLE IF NOT EXISTS spaceBDD.launches (
	id VARCHAR(256) UNIQUE NOT NULL,
    launch_name VARCHAR(256),
    rocket_id VARCHAR(256),
    success BOOL,
    launch_date DATETIME
)
"""

second_query = """
CREATE TABLE IF NOT EXISTS spaceBDD.launch_images (
	id INT NOT NULL,
    launch_id VARCHAR(256) NOT NULL,
    rocket_id VARCHAR(256),
    image_url VARCHAR(256)
)
"""
with engine.connect() as conn:
	conn.execute(text(first_query))
	print('Launch Table Connected')
	try:
		df_launches.to_sql(name='launches', con=engine, if_exists='append', index=False)
	except:
		print("Launches Already Exist")
	
	conn.execute(text(second_query))
	print('Launch Images Table Connected')
	try:
		df_launch_images.to_sql(name='launch_images', con=engine, if_exists='append', index=False)
	except:
		print("Images Already Exist")

conn.close()
print('Closed Database Connection')

