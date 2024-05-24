import sqlalchemy
import pandas as pd 
import requests
import json
from sqlalchemy import text
from datetime import datetime

URL = 'https://api.spacexdata.com/v4/launches'
HOST = "my-aeronautics-db.cb95ufq3bxca.us-east-1.rds.amazonaws.com"
USER = 'admin'
PASS = 'password'
DB = 'spaceBDD'

launch_query = """
	CREATE TABLE IF NOT EXISTS spaceBDD.launches (
		id VARCHAR(256) UNIQUE NOT NULL,
		launch_name VARCHAR(256),
		rocket_id VARCHAR(256),
		success BOOL,
		launch_date DATETIME
	)
	"""

image_query = """
	CREATE TABLE IF NOT EXISTS spaceBDD.launch_images (
		id INT NOT NULL,
		launch_id VARCHAR(256) NOT NULL,
		rocket_id VARCHAR(256),
		image_url VARCHAR(256)
	)
	"""

#Data Validation 
def valid_launch(df: pd.DataFrame):
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
	print("Data valid, proceed to Data Transformations")
	return df

#Validation
def valid_image(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new images. Finishing execution")
		return False 

	# Composite Primary Key Check
	temp = df[['id', 'launch_id']].value_counts(ascending=True).reset_index(name='count')
	for item in pd.Series(temp['count']):
		if item != 1:
			raise Exception("Invalid primary key")
	print("Data valid, proceed to Data Transformations")
	return df

#Extraction
def extract_launches():
	r = requests.get(URL)
	data = r.json() 

	ids = []
	names = []
	rocket_ids = []
	success = []
	dates = []

	for i in range(len(data)):
		curr = data[i]
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
	
	df = pd.DataFrame(launch_dict, columns=['id', 'launch_name', 'rocket_id','success', 'launch_date'])
	return df

def extract_images():
	r = requests.get(URL)
	data = r.json() 
	launch_ids = []
	image_urls = []
	fk_rocket_ids = []
	image_increments = []

	images_dict = {
		'id': image_increments,
		'launch_id': launch_ids,
		'rocket_id': fk_rocket_ids,
		'image_url': image_urls
	}

	for i in range(len(data)):
		curr = data[i]
		for j in range(len(curr['links']['flickr']['original'])):
			image_increments.append(j)
			launch_ids.append(curr['id'])
			image_urls.append(curr['links']['flickr']['original'][j])
			fk_rocket_ids.append(curr['rocket'])

	df = pd.DataFrame(images_dict, columns=['id', 'launch_id', 'rocket_id', 'image_url'])
	return df

#Data Tranformations
def transform_launch(df: pd.DataFrame):
	ts = [int(x) for x in df['launch_date']]
	df['launch_date'] = [datetime.utcfromtimestamp(t).strftime('%Y-%m-%d') for t in ts]

	df['launch_date'] = pd.to_datetime(df['launch_date'])


	df['id'] = df['id'].astype(str)
	df['rocket_id'] = df['rocket_id'].astype(str)
	df['launch_name'] = df['launch_name'].astype(str)
	df['success'] = df['success'].astype(bool)
	return df

def transform_image(df:pd.DataFrame):
	df['launch_id'] = df['launch_id'].astype(str)
	df['rocket_id'] = df['rocket_id'].astype(str)
	df['image_url'] = df['image_url'].astype(str)
	return df


#Loading 
def load(df: pd.DataFrame, query):
	db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

	engine = sqlalchemy.create_engine(db_url)
	with engine.connect() as conn:
		conn.execute(text(query))
		print('Launch Table Connected')
		try:
			df.to_sql(name='launches', con=engine, if_exists='append', index=False)
		except:
			print("Data Already Exists")

	conn.close()
	print('Closed Database Connection')

