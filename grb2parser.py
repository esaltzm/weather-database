import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2 as ps

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

# plt.contourf(ds['crain'])
# plt.colorbar()
# plt.show()

ds_t = ds.get('t')
df = ds_t.to_dataframe()

for var in ['vis', 'gust', 'sde', 'prate', 'crain', 'ltng']:
    ds_var = ds.get(var)
    df_var = ds_var.to_dataframe()
    df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

df.drop(columns=['step', 'surface'])
df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop'})
cols = ['time_start', 'time_stop', 'latitude', 'longitude', 't', 'vis', 'gust', 'sde', 'prate', 'crain', 'ltng'] # temp, visibility, wind gust speed, snow depth, precipitation rate, categorical rain, lightning
df = df[cols]

shift_longitude = lambda lon: lon - 360 if lon > 180 else lon # 0, 360 to -180, 180
convert_temp = lambda t: t - 273.15 # K to C
convert_time = lambda t: int(t.timestamp()) # pd.datetime64 to unix (s since 1970)
round_var = lambda v: round(v)
bool_var = lambda v: True if v > 0.5 else False


df['longitude'] = df['longitude'].apply(shift_longitude)
df['t'] = df['t'].apply(convert_temp)
df['time_start'] = df['time_start'].apply(convert_time)
df['time_stop'] = df['time_stop'].apply(convert_time)
df['vis'] = df['vis'].apply(round_var)
df['crain'] = df['crain'].apply(bool_var)
df['ltng'] = df['ltng'].apply(bool_var)

print(df.head())
print(df.tail())

print('length: ', len(df))