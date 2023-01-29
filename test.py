import cfgrib
import xarray as xr
import pandas as pd

ds_t = xr.open_dataset('/Users/elijahsaltzman/Downloads/rap_130_2023012300.g2/rap_130_20230123_0000_000.grb2', engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'heightAboveGround', 'level': 2}, backend_kwargs={'indexpath': ''})
print(ds_t.data_vars)
ds_t2m = ds_t.get('t2m')
df = ds_t2m.to_dataframe()

ds = xr.open_dataset('/Users/elijahsaltzman/Downloads/rap_130_2023012300.g2/rap_130_20230123_0000_000.grb2', engine='cfgrib', filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'}, backend_kwargs={'indexpath': ''})


