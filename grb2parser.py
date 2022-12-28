import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

plt.contourf(ds['crain'])
plt.colorbar()
plt.show()

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
# print(df_vis.columns)
# for item in list(df_vis.values)[:3]:
#     print(item)

ds_gust = ds.get('gust')
df_gust = ds_gust.to_dataframe()
# print(df_gust.columns)
# for item in list(df_gust.values)[:3]:
#     print(item)

ds_sde = ds.get('sde')
df_sde = ds_sde.to_dataframe()
# print(df_sde.columns)
# for item in list(df_sde.values)[:3]:
#     print(item)

ds_prate = ds.get('prate')
df_prate = ds_prate.to_dataframe()
# print(df_prate.columns)
# for item in list(df_prate.values)[:3]:
#     print(item)

ds_crain = ds.get('crain')
df_crain = ds_crain.to_dataframe()
print(df_crain.columns)
for item in list(df_crain.values)[:3]:
    print(item)
