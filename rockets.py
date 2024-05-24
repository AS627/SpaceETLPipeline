import sqlalchemy
import pandas as pd 
import requests
import json
from datetime import datetime
from sqlalchemy import text

URL = 'https://api.spacexdata.com/v4/rockets'
HOST = "my-aeronautics-db.cb95ufq3bxca.us-east-1.rds.amazonaws.com"
USER = 'admin'
PASS = 'password'
DB = 'spaceBDD'

rocket_query = """
   CREATE TABLE IF NOT EXISTS spaceBDD.rockets (
	id varchar(256) UNIQUE NOT NULL,
	name varchar(256),
    height numeric(18,0),
	mass INT,
	diameter numeric(18,0),
    first_flight DATETIME,
    cost_per_launch INT,
    thrust_to_weight numeric(18,0),
    Isp_s numeric(18,0),
	Isp_v numeric(18,0)
)
"""

image_query = """
CREATE TABLE IF NOT EXISTS spaceBDD.rocket_images (
	id INT NOT NULL ,
    rocket_id VARCHAR(256) NOT NULL,
    image_url varchar(256)
)
"""

def valid_rocket(df: pd.DataFrame):
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
	if df.isnull().values.any():
		raise Exception("Null values found")
	print("Data valid, proceed to Data Transformations")
	return df

def valid_image(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new images. Finishing execution")
		return False 

	# Composite Primary Key Check
	temp = df[['id', 'rocket_id']].value_counts(ascending=True).reset_index(name='count')
	for item in pd.Series(temp['count']):
		if item != 1:
			raise Exception("Invalid primary key")
	print("Data valid, proceed to Data Transformations")
	return df

def extract_rockets():
	r = requests.get(URL)
	data = r.json()

	ids = []
	names = []
	heights = []
	masses = []
	diameters = []
	takeoffs = []
	cost_per_launches = []
	thrust_to_weights = []

	for i in range(len(data)):
		curr = data[i]
		ids.append(curr['id'])
		names.append(curr['name'])
		heights.append(curr['height']['meters'])
		masses.append(curr['mass']['kg'])
		diameters.append(curr['diameter']['meters'])
		takeoffs.append(curr['first_flight'])
		cost_per_launches.append(curr['cost_per_launch'])
		thrust_to_weights.append(curr['engines']['thrust_to_weight'])
	
		rocket_dict = {
		'id': ids,
		'name': names,
		'height':heights,
		'mass':masses,
		'diameter': diameters,
		'first_flight': takeoffs,
		'cost_per_launch':cost_per_launches,
		'thrust_to_weight':thrust_to_weights
	}

	df = pd.DataFrame(rocket_dict, columns=['id', 'name','height', 'mass', 'diameter', 'first_flight', 'cost_per_launch', 'thrust_to_weight'])
	return df


def extract_images():
	r = requests.get(URL)
	data = r.json()

	rockets = []
	image_increment = []
	images = []

	for i in range(len(data)):
		curr = data[i]
		for j in range(len(curr['flickr_images'])):
			image_increment.append(j + 1)
			rockets.append(curr['id'])
			images.append(curr['flickr_images'][j])

	images_dict = {
		'id': image_increment,
		'rocket_id': rockets,
		'image_url': images
	}

	df = pd.DataFrame(images_dict, columns = ['id', 'rocket_id', 'image_url'])
	return df




#Data Transformation
def transform_rocket(df: pd.DataFrame):
	df['first_flight'] = pd.to_datetime(df['first_flight'])
	df['id'] = df['id'].astype(str)
	df['name'] = df['name'].astype(str)

	#Obtain acceleration from T/W ratio
	df['acceleration'] = df['thrust_to_weight'] * 9.8
	return df


def transform_image(df:pd.DataFrame):
	df['rocket_id'] = df['rocket_id'].astype(str)
	df['image_url'] = df['image_url'].astype(str)
	return df

#Loading Stage
def load(df: pd.DataFrame, query):
	db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

	engine = sqlalchemy.create_engine(db_url)


	with engine.connect() as conn:
		conn.execute(text(query))
		print('Table Connected')
		try:
			df.to_sql(name='rockets', con=engine, if_exists='append', index=False)
		except:
			print("Data Already Exists")

	conn.close()
	print('Closed Database Connection')