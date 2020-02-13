import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import Basemap, addcyclic
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch

def plotPavalaCoastline():
	m.readshapefile('/home/kalassak/Desktop/pavala/shp/mainland', 'mainland')
	m.readshapefile('/home/kalassak/Desktop/pavala/shp/lakes', 'lakes')

	patches = []
	for shape in m.mainland:
		patches.append(Polygon(np.array(shape), True))

	ax.add_collection(PatchCollection(patches, facecolor=(0,0,0,0), edgecolor='k', linewidths=2))

	patches_lake = []
	for shape in m.lakes:
		patches_lake.append(Polygon(np.array(shape), True))

	ax.add_collection(PatchCollection(patches_lake, facecolor=(0,0,0,0), edgecolor='k', linewidths=2))

nc = netCDF4.Dataset("../ncout.nc")

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
temps = nc.variables['tas'][:]
us = nc.variables['ua'][:]
vs = nc.variables['va'][:]
qs = nc.variables['hus'][:]

precips = nc.variables['pr'][:]
times = nc.variables['time'][:]

#convert temp to deg F
temps = (temps-273.15)*9/5 + 32

WIND_SAMPLE_RATE = 2

nc.close()

m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,llcrnrlon=0,urcrnrlon=360,resolution='l') #-90 90 -180 180
#m = Basemap(projection='ortho',lon_0=100,lat_0=0,resolution='l') #this doesn't allow contours to be drawn?

taslevels = np.arange(-40, 120, 1)
for i in xrange(len(times)):
	fig = plt.figure(figsize=(18.6, 10.5))
	ax = fig.add_axes((0,0,1,1))
	ax.set_axis_off()

	m.drawcoastlines()

	# plot temperature contours
	plt.contourf(lons, lats, temps[i], levels=taslevels, linewidths=1, cmap='bwr', zorder=0)
	plt.contour(lons, lats, temps[i], levels=taslevels, linewidths=1, colors='k', zorder=1)

	plt.colorbar(fraction=0.025, pad=0.01)
	
	plt.savefig("/home/kalassak/ps-capstone/temp_" + str(i) + ".png", bbox_inches='tight', pad_inches=0, dpi=100)
	plt.close()

	print "plot for " + str(times[i]) + " generated"
	i += 1

#m.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
#m.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
