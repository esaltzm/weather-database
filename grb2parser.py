# import xarray as xr
# import pandas as pd
# import time
import os
import mysql.connector as database
from dotenv import dotenv_values

# Specify environmental variables for MySQL connection, file path where GRB2 files are located

config = dotenv_values('.env')
path = '/Users/elijahsaltzman/grb2'

# Convert GRB2 file to list, each entry containing a row to be inserted into MySQL table

def extract_data(path, folder, filename):

    print(f'Parsing file: {filename}')

    # Retrieve air temperature data (temp at 2 meters height) and convert to Pandas dataframe

    ds_t = xr.open_dataset(os.path.join(path, folder) + '/' + filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'heightAboveGround', 'level': 2}, backend_kwargs={'indexpath': ''})
    ds_t2m = ds_t.get('t2m')
    df = ds_t2m.to_dataframe()

    # Retrieve surface level parameters

    ds = xr.open_dataset(os.path.join(path, folder) + '/' + filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})

    # Retrieve data parameters of interest, merging them to initial air temperature dataframe

    for var in ['gust', 'sde', 'prate', 'ltng']:
        ds_var = ds.get(var)
        df_var = ds_var.to_dataframe()
        df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

    # Drop unneccessary columns, rename and reorder columns

    df.drop(columns=['step', 'heightAboveGround'], axis=1, inplace=True)
    df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop', 't2m': 't'})
    cols = ['time_start', 'time_stop', 'latitude', 'longitude', 't', 'gust', 'sde', 'prate', 'ltng'] # temp, wind gust speed, snow depth, precipitation rate, categorical rain, lightning
    df = df[cols]

    # Define and apply unit conversions to different dataframe columns

    shift_longitude = lambda lon: lon - 360 if lon > 180 else lon # 0, 360 to -180, 180
    convert_temp = lambda t: t - 273.15 # K to C
    convert_time = lambda t: int(t.timestamp()) # pd.datetime64 to unix (s since 1970)
    bit_var = lambda v: True if v > 0.5 else False

    df['longitude'] = df['longitude'].apply(shift_longitude)
    df['t'] = df['t'].apply(convert_temp)
    df['time_start'] = df['time_start'].apply(convert_time)
    df['time_stop'] = df['time_stop'].apply(convert_time)
    df['ltng'] = df['ltng'].apply(bit_var)

    # Convert dataframe to list format and return

    return df.values.tolist()

def write_to_db(rows, cursor):

    # Define MySQL insertion query for each row, initialize start time

    insert_query = """INSERT INTO weather (time_start, latitude, longitude, t, gust, sde, prate, ltng) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    start = time.time()

    # Filter records by whether they appear in initial viewport bounds (from frontend Mapbox component)

    records = []
    for row in rows[8000:130000]: # this range contains bounding box coords
        time_start, time_stop, latitude, longitude, t, gust, sde, prate, ltng = row
        time_start = time_stop
        time_to_remove = time_start
        if latitude >= 22.262387 and latitude <= 50.648574 and longitude >= -127.640625 and longitude <= -64.359375: # AND in default bounding box
            records.append((time_start, latitude, longitude, t, gust, sde, prate, ltng))

    count = len(records)

    # Execute bulk insertion of records list, catching errors and printing runtime and number of records inserted

    try:
        cursor.executemany(insert_query, records)
        print(len(records), 'inserted')
    except database.Error as error:
        print('Failed to overwrite records', error)
    finally:
        print(f'--- {time.time() - start} seconds runtime ---')
        print(f'{count} out of {len(rows)} records were inserted into the database')

# Establish MySQL connection

print(config)
connection = database.connect(user=config['USERNAME'], password=config['PASSWORD'], host=config['HOST'], database='weather')
cursor = connection.cursor()

cursor.execute('SELECT COUNT(*) FROM weather')
print(cursor.fetchone())

# Iterate through directories in GRB2 filepath - each folder contains 24 files for each hour of the day

# for folder in sorted(os.listdir(path), reverse=True):
#     if os.path.isdir(os.path.join(path, folder)):
#         print(f'\n\nParsing folder: {folder}')
#         for filename in sorted(os.listdir(path + '/' + folder)):
#             if filename != '.DS_Store':
#                 hour = filename.split('.')[0][-2:]

#                 # Add every 3rd hour to the database

#                 if int(hour) % 3 == 0:
#                     rows = extract_data(path, folder, filename)
#                     write_to_db(rows, cursor)
                
if connection:
    cursor.close()
    connection.close()
    print('MySQL connection is closed')