import time
import os
import tarfile
import xarray as xr
import pandas as pd
import boto3
import mysql.connector as database
from dotenv import dotenv_values

config = dotenv_values('.env')

def extract_data(filename):

    print(f'Parsing file: {filename}')
    ds = xr.open_dataset(filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})
    ds_t = ds.get('t')
    df = ds_t.to_dataframe()

    for var in ['gust', 'sde', 'prate', 'crain', 'ltng']:
        ds_var = ds.get(var)
        df_var = ds_var.to_dataframe()
        df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

    df.drop(columns=['step', 'surface'])
    df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop'})
    cols = ['time_start', 'time_stop', 'latitude', 'longitude', 't', 'gust', 'sde', 'prate', 'crain', 'ltng'] # temp, wind gust speed, snow depth, precipitation rate, categorical rain, lightning
    df = df[cols]

    shift_longitude = lambda lon: lon - 360 if lon > 180 else lon # 0, 360 to -180, 180
    convert_temp = lambda t: t - 273.15 # K to C
    convert_time = lambda t: int(t.timestamp()) # pd.datetime64 to unix (s since 1970)
    bit_var = lambda v: True if v > 0.5 else False

    df['longitude'] = df['longitude'].apply(shift_longitude)
    df['t'] = df['t'].apply(convert_temp)
    df['time_start'] = df['time_start'].apply(convert_time)
    df['time_stop'] = df['time_stop'].apply(convert_time)
    df['crain'] = df['crain'].apply(bit_var)
    df['ltng'] = df['ltng'].apply(bit_var)

    return df.values.tolist()

def write_to_db(rows, cursor):

    query = """INSERT INTO automation (time_start, latitude, longitude, t, gust, sde, prate, ltng) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    start = time.time()
    count = 0

    records = []

    for row in rows[8000:130000]: # this range contains bounding box coords
        time_start, time_stop, latitude, longitude, t, gust, sde, prate, crain, ltng = row
        time_start = time_stop
        if latitude >= 22.262387 and latitude <= 50.648574 and longitude >= -127.640625 and longitude <= -64.359375:
            records.append((time_start, latitude, longitude, t, gust, sde, prate, ltng))

    count = len(records)

    try:
        cursor.executemany(query, records)
        print(len(records), 'inserted')
    except database.Error as error:
        print('Failed to insert record into table', error)
    finally:
        print(f'--- {time.time() - start} seconds runtime ---')
        print(f'{count} out of {len(rows)} records were inserted into the database')


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    bucket_name = 'noaaweatherdatadaily'
    try:
        objects = s3.list_objects(Bucket=bucket_name)
        if not objects['Contents']:
            return 'Bucket is empty'
        else:
            obj = objects['Contents'][0]
            key = obj['Key']
            if key.endswith('.tar'):
                s3.download_file(bucket_name, key, '/tmp/file.tar')
                with tarfile.open('/tmp/file.tar', 'r') as tar:
                    tar.extractall('/tmp')
                os.remove('/tmp/file.tar')
                print('unzipped and deleted tar file locally')
            else:
                return '.tar file not found'
            connection = database.connect(user=config['USERNAME'], password=config['PASSWORD'], host=config['HOST'], database='weather_db')
            cursor = connection.cursor()
            for filename in os.listdir('/tmp'):
                print(f'filename: {filename}')
                filename = key.split('/')[-1]
                hour = filename.split('.')[0][-2:]
                print(f'hour: {hour}')
                if int(hour) % 3 == 0: # add every 3rd hour to db
                    rows = extract_data('/tmp/' + filename)
                    write_to_db(rows, cursor)
            cursor.close()
            connection.close()
            print('MySQL connection is closed')
            s3.delete_object(Bucket=bucket_name, Key=key)
            print('.tar file deleted')
    except Exception as e:
        return f'exception occurred: {e}'