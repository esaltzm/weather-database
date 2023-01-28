import time
import os
import tarfile
import shutil
import xarray as xr
import pandas as pd
import boto3
import mysql.connector as database

def extract_data(filename):

    print(f'Parsing file: {filename}')
    ds_t = xr.open_dataset(filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'heightAboveGround', 'level': 2}, backend_kwargs={'indexpath': ''})
    ds_t2m = ds_t.get('t2m')
    df = ds_t2m.to_dataframe()

    ds = xr.open_dataset(filename, engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})

    for var in ['gust', 'sde', 'prate', 'crain', 'ltng']:
        ds_var = ds.get(var)
        df_var = ds_var.to_dataframe()
        df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

    df.drop(columns=['step', 'heightAboveGround'], axis=1, inplace=True)
    df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop', 't2m': 't'})
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


def handler(event=None, context=None):
    s3 = boto3.client('s3')
    bucket_name = 'noaaweatherdatadaily'
    objects = s3.list_objects(Bucket=bucket_name)
    try: objects['Contents']
    except: return 'Bucket is empty'
    print('bucket not empty')
    obj = objects['Contents'][0]
    key = obj['Key']
    if key.endswith('.tar'):
        print('found tar file')
        s3.download_file(bucket_name, key, '/tmp/file.tar')
        with tarfile.open('/tmp/file.tar', 'r') as tar:
            tar.extractall('/tmp')
        os.remove('/tmp/file.tar')
        print('unzipped and deleted tar file locally')
    else:
        return '.tar file not found'
    connection = database.connect(user=os.environ['USERNAME'], password=os.environ['PASSWORD'], host=os.environ['HOST'], database='weather_db')
    cursor = connection.cursor()
    for filename in os.listdir('/tmp'):
        print(f'filename: {filename}')
        hour = filename.split('.')[0][-2:]
        print(f'hour: {hour}')
        if int(hour) % 3 == 0: # add every 3rd hour to db
            rows = extract_data('/tmp/' + filename)
            write_to_db(rows, cursor)
    # remove earliest day of data
    cursor.execute('SELECT UNIQUE time_start FROM weather ORDER BY time_start DESC LIMIT 1;')
    latest_time = cursor.fetchone()[0]
    print('latest time: ', latest_time)
    delete_before = latest_time - (365 * 24 * 60 * 60) # one year earlier
    print('will delete before: ', delete_before)
    cursor.execute(f'SELECT UNIQUE time_start FROM weather WHERE time_start <= {delete_before} ORDER BY time_start DESC;')
    # cursor.execute(f'DELETE FROM weather WHERE time_start <= {delete_before}')
    deleted = cursor.fetchall()
    print('will have deleted: ', deleted)
    cursor.close()
    connection.close()
    print('MySQL connection is closed')
    s3.delete_object(Bucket=bucket_name, Key=key)
    print('.tar file deleted')
    clear_tmp()
    print('tmp directory cleared')