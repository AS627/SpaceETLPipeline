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
def check_if_valid_launchpad(df: pd.DataFrame):
	# Check if dataframe is empty
	if df.empty:
		print("No new launchpads. Finishing execution")
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

	

r = requests.get('https://api.spacexdata.com/v4/launchpads')
data = r.json() 

ids = []
names = []
launch_ids = []
status = []
localities = []
regions = []

for i in range(len(data)):
	curr = data[i]
	for j in range(len(curr['launches'])):
		ids.append('id')
		launch_ids.append(curr['launches'][j])
		names.append(curr['full_name'])
		status.append(curr['status'])
		localities.append(curr['locality'])
		regions.append(curr['region'])
        
launchpads_dict = {
	'id': ids,
	'launch_id': launch_ids,
	'pad_name': names,
	'locality': localities,
	'region': regions,
	'activity_status': status
}


df_launchpads = pd.DataFrame(launchpads_dict, columns=['id','launch_id', 'pad_name', 'locality','region', 'activity_status'])

if check_if_valid_launchpad(df_launchpads):
	print("Data valid, proceed to Data Transformations")

#Data Tranformations
df_launchpads['id'] = df_launchpads['id'].astype(str)
df_launchpads['launch_id'] = df_launchpads['launch_id'].astype(str)
df_launchpads['pad_name'] = df_launchpads['pad_name'].astype(str)
df_launchpads['locality'] = df_launchpads['locality'].astype(str)
df_launchpads['region'] = df_launchpads['region'].astype(str)

f = lambda x: True if x == 'active' else False
df_launchpads['activity_status'] = [f(x) for x in df_launchpads['activity_status']]

#Loading Stage
db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

engine = sqlalchemy.create_engine(db_url)

query = """
   CREATE TABLE IF NOT EXISTS spaceBDD.launchpad (
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
	print('Launchpad Table Connected')
	try:
		df_launchpads.to_sql(name='launchpad', con=engine, if_exists='append', index=False)
	except:
		print("Launchpads Already Exist")

conn.close()
print('Closed Database Connection')
