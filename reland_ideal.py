#for this script you will want a python 3.7 conda environment
#install requisite packages with:
#conda install -c conda-forge netcdf4 esmpy=7.1.0 xesmf=0.2.1

import math
import netCDF4
import numpy as np
import xarray as xr
import xesmf as xe

def service_fmt(n):
	# returns a string of the format:
	# ' xxxxx.xxx'
	# for writing arrays data to PlaSim .sra files
	if n >= 10:
		s = ' '*(5-int(math.log(n, 10)))
		t = '%s%.3f' % (s, n)
	else:
		t = '     %.3f' % n
	return t


# cell centers
lons, lats = np.meshgrid(np.linspace(0.5, 10.5, 11), np.linspace(0.5, 10.5, 11))

# cell corners
lon_b, lat_b = np.meshgrid(np.linspace(0, 11, 12), np.linspace(0, 11, 12))

grid_in = {'lon': lons, 'lat': lats, 'lon_b': lon_b, 'lat_b': lat_b}

lons_out, lats_out = np.meshgrid(np.linspace(2.2, 8.8, 5), np.linspace(2.2, 8.8, 5))
lon_out_b, lat_out_b = np.meshgrid(np.linspace(0, 11, 6), np.linspace(0, 11, 6))

grid_out = {'lon': lons_out, 'lat': lats_out, 'lon_b': lon_out_b, 'lat_b': lat_out_b}

regridder = xe.Regridder(grid_in, grid_out, 'conservative')

data = np.zeros((11, 11))
data[3, 3] = 1.0
data[3, 4] = 1.0
data[3, 5] = 1.0
data[4, 3] = 1.0
data[4, 4] = 1.0
data[4, 5] = 1.0
data[5, 3] = 1.0
data[5, 4] = 1.0
data[5, 5] = 1.0

print(data)

data_regrid = regridder(data)

print(data_regrid)
