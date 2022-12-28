import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

# plt.contourf(ds['crain'])
# plt.colorbar()
# plt.show()

# 't', 'vis', 'gust', 'sde', 'prate', 'crain', 'ltng'
# temp, visibility, wind gust speed, snow depth, precipitation rate, categorical rain, lightning

ds_t = ds.get('t')
df = ds_t.to_dataframe()
shift_longitude = lambda lon: (lon - 360) if (lon > 180) else lon 
convert_temp = lambda t: t - 273.15 # K to C
df['longitude'] = df['longitude'].apply(shift_longitude)
df['t'] = df['t'].apply(convert_temp)

for var in ['vis', 'gust', 'sde', 'prate', 'crain', 'ltng']:
    ds_var = ds.get(var)
    df_var = ds_var.to_dataframe()
    df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

df.drop(columns=['step', 'surface'])
df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop'})
cols = ['time_start', 'time_stop', 'latitude', 'longitude', 't', 'vis', 'gust', 'sde', 'prate', 'crain', 'ltng']
df = df[cols]
print(df.columns)
for item in list(df.values)[:3]:
    print(item)
print(df.dtypes)