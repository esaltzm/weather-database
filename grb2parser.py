import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

# plt.contourf(ds['crain'])
# plt.colorbar()
# plt.show()

# 't', 'vis', 'gust', 'sde', 'prate', 'crain', 'ltng'
# temp, visibility, wind gust speed, snow depth, precipitation rate, categorical rain,

ds_t = ds.get('t')
df_t = ds_t.to_dataframe()
# print(df_temp.columns)
shift_longitude = lambda lon: (lon - 360) if (lon > 180) else lon 
convert_temp = lambda t: t - 273.15 # K to C
df_t['longitude'] = df_t['longitude'].apply(shift_longitude)
df_t['t'] = df_t['t'].apply(convert_temp)
# for item in list(df_temp.values)[:3]:
#     print(item)

var_dfs = {'df_t': df_t}

for var in ['vis', 'gust', 'sde', 'prate', 'crain', 'ltng']:
    ds_var = ds.get(var)
    df_var = ds_var.to_dataframe()
    var_dfs['df_' + var] = df_var

print(var_dfs)

