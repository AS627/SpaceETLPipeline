import sqlalchemy
import pandas as pd 
import requests
import json
from datetime import datetime
from sqlalchemy import text

HOST = "my-aeronautics-db.cb95ufq3bxca.us-east-1.rds.amazonaws.com"
USER = 'admin'
PASS = 'password'
DB = 'spaceBDD'

def check_if_valid_rocket(df: pd.DataFrame):
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
	return True

def check_if_valid_image(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new images. Finishing execution")
		return False 

	# Composite Primary Key Check
	temp = df[['id', 'rocket_id']].value_counts(ascending=True).reset_index(name='count')
	for item in pd.Series(temp['count']):
		if item != 1:
			raise Exception("Invalid primary key")
	return True

r = requests.get('https://api.spacexdata.com/v4/rockets')
data = r.json()


ids = []
names = []
heights = []
masses = []
diameters = []
images = []
takeoffs = []
cost_per_launches = []
thrust_to_weights = []


rockets = []
image_increment = []

#Extract data from SpaceX API
for i in range(len(data)):
	curr = data[i]
	for j in range(len(curr['flickr_images'])):
		image_increment.append(j + 1)
		rockets.append(curr['id'])
		images.append(curr['flickr_images'][j])

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


images_dict = {
      'id': image_increment,
      'rocket_id': rockets,
      'image_url': images
}



df_rocket = pd.DataFrame(rocket_dict, columns=['id', 'name','height', 'mass', 'diameter', 'first_flight', 'cost_per_launch', 'thrust_to_weight'])
df_images = pd.DataFrame(images_dict, columns = ['id', 'rocket_id', 'image_url'])

if check_if_valid_rocket(df_rocket):
    print("Data valid, proceed to Data Transformations")

if check_if_valid_image(df_images):
    print("Data valid, proceed to Data Transformations")


#Data Transformation
df_rocket['first_flight'] = pd.to_datetime(df_rocket['first_flight'])
df_rocket['id'] = df_rocket['id'].astype(str)
df_rocket['name'] = df_rocket['name'].astype(str)

#Obtain acceleration from T/W ratio
df_rocket['acceleration'] = df_rocket['thrust_to_weight'] * 9.8


df_images['rocket_id'] = df_images['rocket_id'].astype(str)
df_images['image_url'] = df_images['image_url'].astype(str)

#Loading Stage
db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

engine = sqlalchemy.create_engine(db_url)

first_query = """
   CREATE TABLE IF NOT EXISTS spaceBDD.rockets (
	id varchar(256) UNIQUE NOT NULL,
	name varchar(256),
    height numeric(18,0),
	mass INT,
	diameter numeric(18,0),
    first_flight DATETIME,
    cost_per_launch INT,
    thrust_to_weight numeric(18,0),
    acceleration numeric(18,0)
)
"""

second_query = """
CREATE TABLE IF NOT EXISTS spaceBDD.rocket_images (
	id INT NOT NULL ,
    rocket_id VARCHAR(256) NOT NULL,
    image_url varchar(256)
)
"""
with engine.connect() as conn:
	conn.execute(text(first_query))
	print('Rockets Table Connected')
	try:
		df_rocket.to_sql(name='rockets', con=engine, if_exists='append', index=False)
	except:
		print("Rockets Already Exist")
	
	conn.execute(text(second_query))
	print('Rocket Images Table Connected')
	try:
		df_images.to_sql(name='rocket_images', con=engine, if_exists='append', index=False)
	except:
		print("Images Already Exist")

conn.close()
print('Closed Database Connection')