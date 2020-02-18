#for this script you will want a python 3.7 conda environment
#install requisite packages with:
#conda install -c conda-forge netcdf4 esmpy=7.1.0 xesmf=0.2.1

import math
import netCDF4
import numpy as np
import xarray as xr
import xesmf as xe

def service_fmt_elev(n):
	# returns a string of the format:
	# ' xxxxx.xxx'
	# for writing topography data to PlaSim .sra files
	if n >= 10:
		s = ' '*(5-int(math.log(n, 10)))
		t = '%s%.3f' % (s, n)
	else:
		t = '     %.3f' % n
	return t

def service_fmt_lsm(n):
	# returns a string of the format:
	# '  x.xxxxxx'
	# for writing fractional land data to PlaSim .sra files
	t = '  %.6f' % n
	return t

OPT = 'lsm' #'elev' or 'lsm'

#PlaSim uses GTOPO30 but this dataset is from http://research.jisao.washington.edu/data_sets/elevation/
if OPT == 'elev':
	nc = netCDF4.Dataset("../nc/elev.0.25-deg.nc")
elif OPT == 'lsm':
	nc = netCDF4.Dataset("../nc/fractional_land.0.25-deg.nc")

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
data = nc.variables['data'][0,:]

if OPT == 'elev':
	#remove ocean bathymetry (negative elevation)
	data = np.where(data >= 0.0, data, 0.0)

nc.close()

nc2 = netCDF4.Dataset("../nc/ncout_small.nc")

lats_n256 = nc2.variables['lat'][:]
lons_n256 = nc2.variables['lon'][:]

nc2.close()

#create grid boundary arrays
lat_avg = 0.5*(lats[1:] + lats[:-1])
lat_avg = np.concatenate(([90.0], lat_avg, [-90.0]))
lon_avg = 0.5*(lons[1:] + lons[:-1])
lon_avg = np.concatenate(([0.0], lon_avg, [360.0]))

lon_b, lat_b = np.meshgrid(lon_avg, lat_avg)

lat_n256_avg = 0.5*(lats_n256[1:] + lats_n256[:-1])
lat_n256_avg = np.concatenate(([90.0], lat_n256_avg, [-90.0]))
lon_n256_avg = 0.5*(lons_n256[1:] + lons_n256[:-1])
lon_n256_avg = np.concatenate(([0.0], lon_n256_avg, [360.0]))

lon_n256_b, lat_n256_b = np.meshgrid(lon_n256_avg, lat_n256_avg)

print(lat_n256_b)

grid_in = {'lon': lons, 'lat': lats, 'lon_b': lon_b, 'lat_b': lat_b}

grid_out = {'lon': lons_n256, 'lat': lats_n256, 'lon_b': lon_n256_b, 'lat_b': lat_n256_b}

regridder = xe.Regridder(grid_in, grid_out, 'conservative')

data_n256 = regridder(data)

#data_n256 = g(lons_n256, lats_n256)
#data_n256 = np.flip(data_n256, axis=0)

print(data_n256.shape)

#flatten array for output
print(data_n256)
data_n256 = data_n256.flatten()
print(data_n256)

if OPT == 'elev':
	#geometric height -> geopotential height
	#we will try g_0*z
	g_0 = 9.8066 #add more sig figs
	gpms = g_0*data_n256
elif OPT == 'lsm':
	lsms = data_n256

#write service file
print("writing service file...")

if OPT == 'elev':
	f = open("n032_elev.sra", "w")
	f.write("       129         0  20070101         0        64        32         0         0\n")

	l = ''
	for i, gpm in enumerate(gpms):
		l += service_fmt_elev(gpm)
		if i % 8 == 7:
			l += '\n'
			f.write(l)
			l = ''
elif OPT == 'lsm':
	f = open("n032_lsm.sra", "w")
	f.write("       172         0  20090101         0        64        32         0         0\n")

	l = ''
	for i, lsm in enumerate(lsms):
		l += service_fmt_lsm(lsm)
		if i % 8 == 7:
			l += '\n'
			f.write(l)
			l = ''

f.close()
