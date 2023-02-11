import time
import os
import tarfile
import shutil
import xarray as xr
import pandas as pd
import boto3
import mysql.connector as database

# Convert GRB2 file to list, each entry containing a row to be inserted into MySQL table

def extract_data(filename):

    print(f'Parsing file: {filename}')

    # Retrieve air temperature data (temp at 2 meters height) and convert to Pandas dataframe

    ds_t = xr.open_dataset(filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'heightAboveGround', 'level': 2}, backend_kwargs={'indexpath': ''})
    ds_t2m = ds_t.get('t2m')
    df = ds_t2m.to_dataframe()

    # Retrieve surface level parameters

    ds = xr.open_dataset(filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})

    # Retrieve data parameters of interest, merging them to initial air temperature dataframe

    for var in ['gust', 'sde', 'prate', 'ltng']:
        ds_var = ds.get(var)
        df_var = ds_var.to_dataframe()
        df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

    # Drop unneccessary columns, rename and reorder columns

    df.drop(columns=['step', 'heightAboveGround'], axis=1, inplace=True)
    df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop', 't2m': 't'})
    cols = ['time_start', 'time_stop', 'latitude', 'longitude', 't', 'gust', 'sde', 'prate', 'ltng'] # temp, wind gust speed, snow depth, precipitation rate, lightning
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

    query = """INSERT INTO weather (time_start, latitude, longitude, t, gust, sde, prate, ltng) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    start = time.time()

    # Filter records by whether they appear in initial viewport bounds (from frontend Mapbox component)

    records = []
    for row in rows[8000:130000]: # this range contains bounding box coords
        time_start, time_stop, latitude, longitude, t, gust, sde, prate, ltng = row
        time_start = time_stop
        if latitude >= 22.262387 and latitude <= 50.648574 and longitude >= -127.640625 and longitude <= -64.359375:
            records.append((time_start, latitude, longitude, t, gust, sde, prate, ltng))
    count = len(records)

    # Execute bulk insertion of records list, catching errors and printing runtime and number of records inserted

    try:
        cursor.executemany(query, records)
        print(len(records), 'inserted')
    except database.Error as error:
        print('Failed to insert record into table', error)
    finally:
        print(f'--- {time.time() - start} seconds runtime ---')
        print(f'{count} out of {len(rows)} records were inserted into the database')

# Clear tmp directory of unzipped GRB2 files after parsing

def clear_tmp():
    for filename in os.listdir('/tmp'):
        file_path = os.path.join('/tmp', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path} - {e}')

# Main lambda function handler

def handler(event=None, context=None):

    # Find data from bucket uploaded by the download lambda function

    s3 = boto3.client('s3')
    bucket_name = 'noaaweatherdatadaily'
    objects = s3.list_objects(Bucket=bucket_name)
    if objects.get('Contents'):
        obj = objects['Contents'][0]
    else:
        print('Bucket is empty')
        return 'Bucket is empty'

    # Find tar file from bucket, extract all contents to /tmp directory

    key = obj['Key']
    if key.endswith('.tar'):
        print('found tar file')
        s3.download_file(bucket_name, key, '/tmp/file.tar')
        with tarfile.open('/tmp/file.tar', 'r') as tar:
            tar.extractall('/tmp')
        os.remove('/tmp/file.tar')
        print('unzipped and deleted tar file locally')
    else:
        print('.tar file not found')
        return '.tar file not found'

    # Connect to MySQL database

    connection = database.connect(user=os.environ['USERNAME'], password=os.environ['PASSWORD'], host=os.environ['HOST'], database='weather')
    cursor = connection.cursor()

    # Iterate through unzipped GRB2 files, processing only every 3rd hourly file

    for filename in os.listdir('/tmp'):
        print(f'filename: {filename}')
        hour = filename.split('.')[0][-2:]
        print(f'hour: {hour}')
        if int(hour) % 3 == 0: # add every 3rd hour to db
            rows = extract_data('/tmp/' + filename)
            write_to_db(rows, cursor)

    # Fetch latest time in the database after insertion of new data

    cursor.execute('SELECT UNIQUE time_start FROM weather ORDER BY time_start DESC LIMIT 1;')
    latest_time = cursor.fetchone()[0]
    print('latest time: ', latest_time)

    # Delete all data over 1 year old (caps database size at 1 year)

    delete_before = latest_time - (365 * 24 * 60 * 60) # one year earlier
    print('will delete before: ', delete_before)
    cursor.execute(f'DELETE FROM weather WHERE time_start <= {delete_before};')
    connection.commit()
    deleted = cursor.rowcount
    print('deleted: ', deleted)

    # After deletion of older rows, fetch earliest time in the database

    cursor.execute('SELECT UNIQUE time_start FROM weather ORDER BY time_start ASC LIMIT 1;')
    earliest_time = cursor.fetchone()[0]

    # Clear time_range table and insert earliest and latest times (used on front end)

    cursor.execute('TRUNCATE TABLE time_range')
    cursor.execute(f'INSERT INTO time_range (earliest, latest) VALUES ({earliest_time}, {latest_time})')
    cursor.execute('SELECT * FROM time_range')
    time_range = cursor.fetchone()
    print('time_range set to: ', time_range)

    # Close connection, delete GRB2 zip file from S3 bucket, clear /tmp directory for next download

    cursor.close()
    connection.close()
    print('MySQL connection is closed')
    s3.delete_object(Bucket=bucket_name, Key=key)
    print('.tar file deleted')
    clear_tmp()
    print('tmp directory cleared')
    return 'successfully parsed data and inserted into db'