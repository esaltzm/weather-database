import xarray as xr
import pandas as pd
import time
import os
import mysql.connector as database
from in_conus import *
from dotenv import dotenv_values

config = dotenv_values('.env')
path = '/Volumes/Untitled/grb2_files_NEW'

def extract_data(path, folder, filename):

    print(f'Parsing file: {filename}')
    ds = xr.open_dataset(os.path.join(path, folder) + '/' + filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})
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

    query = """INSERT INTO weather (time_start, latitude, longitude, t, gust, sde, prate, ltng) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    start = time.time()
    count = 0

    records = []

    for row in rows[8000:130000]: # this range contains bounding box coords
        time_start, time_stop, latitude, longitude, t, gust, sde, prate, crain, ltng = row
        time_start = time_stop
        if latitude >= 22.262387 and latitude <= 50.648574 and longitude >= -127.640625 and longitude <= -64.359375: # AND in default bounding box
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


connection = database.connect(user=config['USERNAME'], password=config['PASSWORD'], host=config['HOST'], database='weather_db')
cursor = connection.cursor()

for folder in sorted(os.listdir(path)):
    if os.path.isdir(os.path.join(path, folder)):
        print(f'Parsing folder: {folder}')
        for filename in sorted(os.listdir('/Volumes/Untitled/grb2_files_NEW/' + folder)):
            if filename != '.DS_Store':
                hour = filename.split('.')[0][-2:]
                print(hour)
                if int(hour) % 3 == 0: # add every 3rd hour to db
                    rows = extract_data(path, folder, filename)
                    write_to_db(rows, cursor)
                
if connection:
    cursor.close()
    connection.close()
    print('MySQL connection is closed')