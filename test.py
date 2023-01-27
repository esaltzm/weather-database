import cfgrib
import xarray as xr
import pandas as pd

ds_t = xr.open_dataset('/Users/elijahsaltzman/Downloads/rap_130_2023012300.g2/rap_130_20230123_0000_000.grb2', engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'heightAboveGround', 'level': 2}, backend_kwargs={'indexpath': ''})
ds_t2m = ds_t.get('t2m')
df = ds_t2m.to_dataframe()

ds = xr.open_dataset('/Users/elijahsaltzman/Downloads/rap_130_2023012300.g2/rap_130_20230123_0000_000.grb2', engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})

for var in ['gust', 'sde', 'prate', 'crain', 'ltng']:
    ds_var = ds.get(var)
    df_var = ds_var.to_dataframe()
    df = pd.merge(df, df_var[var], left_index=True, right_index=True, how='outer')

df.drop(columns=['step', 'heightAboveGround'], axis=1, inplace=True)
df = df.rename(columns={'time': 'time_start', 'valid_time': 'time_stop', 't2m': 't'})

print(df.head(5))