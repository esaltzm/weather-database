import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

# for item in ds:
#     print(f'{item}, {ds[item].attrs["long_name"]}, {ds[item].attrs["units"]}')

# plt.contourf(ds['t'])
# plt.colorbar()
# plt.show()

ds = ds.get('t')
df = ds.to_dataframe()
print(type(df))
print(df.columns)
# for item in list(df.values)[:3]:
#     print(item)
shift_longitude = lambda lon: (lon - 360) if (lon > 180) else lon
convert_temp = lambda t: 1.8 * (t - 273) + 32
df['longitude'] = df['longitude'].apply(shift_longitude)
df['t'] = df['t'].apply(convert_temp)
for item in list(df.values)[:3]:
    print(item)
