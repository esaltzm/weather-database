import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

# plt.contourf(ds['vis'])
# plt.colorbar()
# plt.show()

# 't', 'vis', 'gust', 'sde', 'prate', 'crain', 'ltng'
# temp, visibility, wind gust speed, snow depth, precipitation rate, categorical rain,

ds_temp = ds.get('t')
df_temp = ds_temp.to_dataframe()
# print(df_temp.columns)
shift_longitude = lambda lon: (lon - 360) if (lon > 180) else lon 
convert_temp = lambda t: t - 273.15 # K to C
df_temp['longitude'] = df_temp['longitude'].apply(shift_longitude)
df_temp['t'] = df_temp['t'].apply(convert_temp)
# for item in list(df_temp.values)[:3]:
#     print(item)

ds_vis = ds.get('vis')
df_vis = ds_vis.to_dataframe()
print(df_vis.columns)
for item in list(df_vis.values)[:3]:
    print(item)
