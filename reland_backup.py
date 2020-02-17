import math
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic
from matplotlib.colors import BoundaryNorm
from scipy import interpolate

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

print data

nc.close()

nc2 = netCDF4.Dataset("../nc/ncout_small.nc")

lats_n256 = nc2.variables['lat'][:]
lons_n256 = nc2.variables['lon'][:]

nc2.close()

g = interpolate.interp2d(lons, lats, data)

data_n256 = g(lons_n256, lats_n256)
data_n256 = np.flip(data_n256, axis=0)

print lats_n256
print data_n256.shape

#plot

print "plotting..."

m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,llcrnrlon=0,urcrnrlon=360,resolution='l')

zlevels = np.arange(-6000, 6000, 10)

fig = plt.figure(figsize=(18.6, 10.5))
ax = fig.add_axes((0,0,1,1))
ax.set_axis_off()

m.drawcoastlines()

# plot pres contours & 1000 hPa wind
cmap = plt.get_cmap('Set1')
norm = BoundaryNorm(zlevels, ncolors=cmap.N)
plt.pcolormesh(lons_n256, lats_n256, data_n256, cmap=cmap, norm=norm, zorder=0)

plt.colorbar(fraction=0.025, pad=0.01)

plt.savefig("/home/kalassak/ps-capstone/topo.png", bbox_inches='tight', pad_inches=0, dpi=100)
plt.close()

#geometric -> geopotential we will try g_0*z
print data_n256
data_n256 = data_n256.flatten()
print data_n256

g_0 = 9.8066 #add more sig figs
gpms = data_n256*g_0

#write service file
print "writing service file..."

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
		
