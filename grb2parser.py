import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('./grb2_files/rap_130_20221220_0000_001.grb2', engine="cfgrib", filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})

# for item in ds:
#     print(f'{item}, {ds[item].attrs["long_name"]}, {ds[item].attrs["units"]}')

plt.contourf(ds['t'])
plt.colorbar()
plt.show()