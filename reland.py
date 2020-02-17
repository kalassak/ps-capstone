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


#PlaSim uses GTOPO30 but this dataset is from http://research.jisao.washington.edu/data_sets/elevation/
nc = netCDF4.Dataset("../nc/elev.0.25-deg.nc")

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
data = nc.variables['data'][0,:]

data = np.where(data >= 0.0, data, 0.0)

nc.close()

nc2 = netCDF4.Dataset("../nc/ncout_small.nc")

lats_n256 = nc2.variables['lat'][:]
lons_n256 = nc2.variables['lon'][:]

nc2.close()

grid_in = {'lon': lons, 'lat': lats}

grid_out = {'lon': lons_n256, 'lat': lats_n256}

regridder = xe.Regridder(grid_in, grid_out, 'bilinear')

data_n256 = regridder(data)

#data_n256 = g(lons_n256, lats_n256)
#data_n256 = np.flip(data_n256, axis=0)

print(lats_n256)
print(data_n256.shape)

#geometric -> geopotential we will try g_0*z
print(data_n256)
data_n256 = data_n256.flatten()
print(data_n256)

g_0 = 9.8066 #add more sig figs
gpms = data_n256*g_0

#write service file
print("writing service file...")

f = open("n032_out.sra", "w")

f.write("       129         0  20070101         0        64        32         0         0\n")

l = ''
for i, gpm in enumerate(gpms):
	l += service_fmt(gpm)
	if i % 8 == 7:
		l += '\n'
		f.write(l)
		l = ''

f.close()
