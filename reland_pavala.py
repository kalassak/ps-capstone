#for this script you will want a python 3.7 conda environment
#install requisite packages with:
#conda install -c conda-forge netcdf4 esmpy=7.1.0 xesmf=0.2.1
#then install matplotlib

#note to self: run with conda environment 'reland2'

import math
import netCDF4
import numpy as np
import xarray as xr
import xesmf as xe
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib.colors import BoundaryNorm

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

OPT = 'elev' #'elev' or 'lsm'
RES = 32 #32 or 256

img = imread('./pavala/Pavala_225.png')*255
print(img.shape)

print(img[521,2564])

elev = []
for i, imgrow in enumerate(img):
	if i % 100 == 0:
		print(i)
	for j, imgcolors in enumerate(imgrow):
		r = int(imgcolors[0])
		g = int(imgcolors[1])
		b = int(imgcolors[2])
		#sea
		if r == 182 and g == 220 and b == 244:
			elev.append(0.)
		elif r == 196 and g == 223 and b == 239:
			elev.append(0.)
		elif r == 217 and g == 231 and b == 246:
			elev.append(0.)
		#coastline
		elif r == 0 and g == 0 and b == 0:
			elev.append(1.)
		elif r == 0 and g == 0 and b == 34:
			elev.append(1.)
		#land
		elif r == 105 and g == 255 and b == 0:
			elev.append(50.)
		elif r == 129 and g == 229 and b == 22: #NEW COLOR
			elev.append(175.)
		elif r == 127 and g == 216 and b == 32:
			elev.append(375.)
		elif r == 120 and g == 204 and b == 30:
			elev.append(625.)
		elif r == 111 and g == 188 and b == 28:
			elev.append(875.)
		elif r == 96 and g == 160 and b == 24:
			elev.append(1125.)
		elif r == 143 and g == 160 and b == 24:
			elev.append(1375.)
		elif r == 165 and g == 183 and b == 27:
			elev.append(1625.)
		elif r == 186 and g == 206 and b == 30:
			elev.append(1875.)
		elif r == 204 and g == 226 and b == 34:
			elev.append(2125.)
		elif r == 225 and g == 249 and b == 37:
			elev.append(2375.)
		elif r == 225 and g == 194 and b == 37:
			elev.append(2625.)
		elif r == 206 and g == 177 and b == 35:
			elev.append(2875.)
		elif r == 183 and g == 158 and b == 31:
			elev.append(3125.)
		elif r == 165 and g == 142 and b == 28:
			elev.append(3375.)
		elif r == 145 and g == 125 and b == 24:
			elev.append(3625.)
		elif r == 99 and g == 85 and b == 16:
			elev.append(3875.)
		elif r == 145 and g == 74 and b == 24:
			elev.append(4250.)
		elif r == 163 and g == 81 and b == 27:
			elev.append(4750.)
		elif r == 178 and g == 89 and b == 30:
			elev.append(5250.)
		elif r == 193 and g == 97 and b == 32:
			elev.append(5750.)
		elif r == 206 and g == 56 and b == 43:
			elev.append(6500.)
		elif r == 234 and g == 64 and b == 49:
			elev.append(7500.)
		#land below sea level
		elif r == 102 and g == 255 and b == 163:
			elev.append(-50.)
		elif r == 91 and g == 229 and b == 144:
			elev.append(-175.)
		elif r == 81 and g == 204 and b == 128:
			elev.append(-375.)
		elif r == 71 and g == 178 and b == 110:
			elev.append(-625.)
		elif r == 61 and g == 153 and b == 94:
			elev.append(-875.)
		elif r == 51 and g == 127 and b == 76:
			elev.append(-1125.)
		elif r == 41 and g == 102 and b == 60:
			elev.append(-1375.)
		elif r == 31 and g == 76 and b == 44:
			elev.append(-1625.)
		elif r == 20 and g == 51 and b == 29:
			elev.append(-1875.)
		#invalid color
		else:
			print('invalid color at (%d,%d)' % (i, j))

elev = np.array(elev)
elev = elev.reshape(img.shape[:-1])

print(elev[521,2564])

#create lat/lon bounds and center points for pixel grid
lon_b, lat_b = np.meshgrid(np.linspace(0., 360., elev.shape[1]+1), np.linspace(90., -90., elev.shape[0]+1))

lon_avg = 0.5*(lon_b[0,1:] + lon_b[0,:-1])
lat_avg = 0.5*(lat_b[1:,0] + lat_b[:-1,0])

lons, lats = np.meshgrid(lon_avg, lat_avg)

#load in T21 lat/lon grid
nc2 = netCDF4.Dataset("../nc/ncout_small.nc")

lats_n256 = nc2.variables['lat'][:]
lons_n256 = nc2.variables['lon'][:]

nc2.close()

#and calculate its boundaries

lat_n256_avg = 0.5*(lats_n256[1:] + lats_n256[:-1])
lat_n256_avg = np.concatenate(([90.0], lat_n256_avg, [-90.0]))
lon_n256_avg = 0.5*(lons_n256[1:] + lons_n256[:-1])
lon_n256_avg = np.concatenate(([0.0], lon_n256_avg, [360.0]))

lon_n256_b, lat_n256_b = np.meshgrid(lon_n256_avg, lat_n256_avg)

print(lons.shape)
print(lon_b.shape)
print(lons_n256.shape)
print(lon_n256_b.shape)

grid_in = {'lon': lons, 'lat': lats, 'lon_b': lon_b, 'lat_b': lat_b}

grid_out = {'lon': lons_n256, 'lat': lats_n256, 'lon_b': lon_n256_b, 'lat_b': lat_n256_b}

regridder = xe.Regridder(grid_in, grid_out, 'conservative', reuse_weights=True)

data_n256 = regridder(elev)

#data_n256 = g(lons_n256, lats_n256)
#data_n256 = np.flip(data_n256, axis=0)

print(data_n256.shape)

#plot
if OPT == 'elev':
	zlevels = np.arange(-6000, 6000, 10)
elif OPT == 'lsm':
	zlevels = np.arange(0, 1, 0.01)

fig = plt.figure(figsize=(18.6, 10.5))
ax = fig.add_axes((0,0,1,1))
ax.set_axis_off()

cmap = plt.get_cmap('bwr')
norm = BoundaryNorm(zlevels, ncolors=cmap.N)
plt.pcolormesh(lons_n256, lats_n256, data_n256, cmap=cmap, norm=norm, zorder=0)

plt.colorbar(fraction=0.025, pad=0.01)

plt.savefig("/home/kalassak/ps-capstone/scripts/pavala/topo.png", bbox_inches='tight', pad_inches=0, dpi=100)
plt.close()

#flatten array for output
print(data_n256)
data_n256 = data_n256.flatten()
print(data_n256)

'''

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
	if RES == 32:
		f = open("n032_elev.sra", "w")
		f.write("       129         0  20070101         0        64        32         0         0\n")
	elif RES == 256:
		f = open("n256_elev.sra", "w")
		f.write("       129         0  20090101        -1       512       256         0         0\n")

	l = ''
	for i, gpm in enumerate(gpms):
		l += service_fmt_elev(gpm)
		if i % 8 == 7:
			l += '\n'
			f.write(l)
			l = ''
elif OPT == 'lsm':
	if RES == 32:
		f = open("n032_lsm.sra", "w")
		f.write("       172         0  20090101         0        64        32         0         0\n")
	elif RES == 256:
		f = open("n256_lsm.sra", "w")
		f.write("       172         0  20090101        -1       512       256         0         0\n")

	l = ''
	for i, lsm in enumerate(lsms):
		l += service_fmt_lsm(lsm)
		if i % 8 == 7:
			l += '\n'
			f.write(l)
			l = ''

f.close()
'''
