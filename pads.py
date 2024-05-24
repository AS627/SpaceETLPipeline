import sqlalchemy
import pandas as pd 
import requests
import json
from sqlalchemy import text
from datetime import datetime

LANDPAD_URL = 'https://api.spacexdata.com/v4/landpads'
LAUNCHPAD_URL = 'https://api.spacexdata.com/v4/launchpads'
HOST = "my-aeronautics-db.cb95ufq3bxca.us-east-1.rds.amazonaws.com"
USER = 'admin'
PASS = 'password'
DB = 'spaceBDD'

query = """
    CREATE TABLE IF NOT EXISTS spaceBDD.pads (
        id VARCHAR(256) NOT NULL,
        launch_id VARCHAR(256) NOT NULL,
        pad_name VARCHAR(256),
        locality VARCHAR(256),
        region VARCHAR(256),
        activity_status BOOL,
        type VARCHAR(50),
        PRIMARY KEY (id, launch_id, type)
    )
    """
# Data Validation
def validate(df: pd.DataFrame):
    # Check if dataframe is empty
    if df.empty:
        print("No new pads. Finishing execution")
        return False 
    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")
    
    # Composite Primary Key Check
    temp = df[['id', 'launch_id', 'type']].value_counts(ascending=True).reset_index(name='count')
    for item in pd.Series(temp['count']):
        if item != 1:
            raise Exception("Invalid primary key")
    print("Data valid, proceed to Data Transformations")
    return df

# Extraction
def extract(url, pad_type):
    r = requests.get(url)
    data = r.json()

    ids = []
    names = []
    launch_ids = []
    status = []
    localities = []
    regions = []
    types = []

    for i in range(len(data)):
        curr = data[i]
        for j in range(len(curr['launches'])):
            ids.append(curr['id'])
            launch_ids.append(curr['launches'][j])
            names.append(curr['full_name'])
            status.append(curr['status'])
            localities.append(curr['locality'])
            regions.append(curr['region'])
            types.append(pad_type)
            
    pads_dict = {
        'id': ids,
        'launch_id': launch_ids,
        'pad_name': names,
        'locality': localities,
        'region': regions,
        'activity_status': status,
        'type': types
    }

    df = pd.DataFrame(pads_dict, columns=['id', 'launch_id', 'pad_name', 'locality', 'region', 'activity_status', 'type'])
    return df

# Data Transformation
def transform(df: pd.DataFrame):
    df['id'] = df['id'].astype(str)
    df['launch_id'] = df['launch_id'].astype(str)
    df['pad_name'] = df['pad_name'].astype(str)
    df['locality'] = df['locality'].astype(str)
    df['region'] = df['region'].astype(str)
    df['type'] = df['type'].astype(str)

    f = lambda x: True if x == 'active' else False
    df['activity_status'] = [f(x) for x in df['activity_status']]
    return df

# Loading Phase
def load(df: pd.DataFrame):
    db_url = f'mysql://{USER}:{PASS}@{HOST}:{3306}/{DB}'

    engine = sqlalchemy.create_engine(db_url)

    with engine.connect() as conn:
        conn.execute(text(query))
        print('Pads Table Connected')
        try:
            df.to_sql(name='pads', con=engine, if_exists='append', index=False)
        except Exception as e:
            print(f"Error: {e}")
            print("Pads Already Exist")

    conn.close()
    print('Closed Database Connection')

# Main ETL function
def etl():
    landpads_df = extract(LANDPAD_URL, 'landpad')
    launchpads_df = extract(LAUNCHPAD_URL, 'launchpad')
    
    combined_df = pd.concat([landpads_df, launchpads_df])
    
    if validate(combined_df):
        transformed_df = transform(combined_df)
        load(transformed_df)

# Run the ETL process
etl()
