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
def check_if_valid_landpad(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new landpads. Finishing execution")
		return False 
	# Check for nulls
	if df.isnull().values.any():
		raise Exception("Null values found")

	# Composite Primary Key Check
	temp = df[['id', 'launch_id']].value_counts(ascending=True).reset_index(name='count')
	for item in pd.Series(temp['count']):
		if item != 1:
			raise Exception("Invalid primary key")
	return True


r = requests.get('https://api.spacexdata.com/v4/landpads')
data = r.json() 

ids = []
names = []
status = []
locality = []
regions = []
launches= []

for i in range(len(data)):
    curr = data[i]
    for j in range(len(curr['launches'])):
        ids.append(curr['id'])
        launches.append(curr['launches'][j])
        names.append(curr['full_name'])
        status.append(curr['status'])
        locality.append(curr['locality'])
        regions.append(curr['region'])

landpads_dict = {
	'id': ids,
	'launch_id': launches,
	'pad_name': names,
	'locality': locality,
	'region': regions,
	'activity_status': status
}

df_landpads = pd.DataFrame(landpads_dict, columns=['id','launch_id', 'pad_name', 'locality','region', 'activity_status'])

if check_if_valid_landpad(df_landpads):
	print("Data valid, proceed to Data Transformations")

#Data Transformation
df_landpads['id'] = df_landpads['id'].astype(str)
df_landpads['launch_id'] = df_landpads['launch_id'].astype(str)
df_landpads['pad_name'] = df_landpads['pad_name'].astype(str)
df_landpads['locality'] = df_landpads['locality'].astype(str)
df_landpads['region'] = df_landpads['region'].astype(str)

f = lambda x: True if x == 'active' else False
df_landpads['activity_status'] = [f(x) for x in df_landpads['activity_status']]

#Loading Phase
db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

engine = sqlalchemy.create_engine(db_url)

query = """
   CREATE TABLE IF NOT EXISTS spaceBDD.landpad (
	id VARCHAR(256) NOT NULL,
    launch_id VARCHAR(256) NOT NULL,
    pad_name VARCHAR(256),
    locality VARCHAR(256),
    region VARCHAR(256),
    activity_status BOOL
)
"""

with engine.connect() as conn:
	conn.execute(text(query))
	print('Landpad Table Connected')
	try:
		df_landpads.to_sql(name='landpad', con=engine, if_exists='append', index=False)
	except:
		print("Landpads Already Exist")

conn.close()
print('Closed Database Connection')