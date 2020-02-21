import math
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic

SEARCH = 5

nc = netCDF4.Dataset("../nc/ncout.nc")

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
qs = nc.variables['hus'][:]
us = nc.variables['ua'][:]
vs = nc.variables['va'][:]

times = nc.variables['time'][:]

nc.close()

START_TIME = 37*4+0 #37 00
END_TIME = 37*4+0 #37 12
SURFACE_WIND_LEVEL = 5 #1000 hPa
UPPER_WIND_LEVEL = 1 #250 hPa

for TIME in xrange(START_TIME, END_TIME+1):
	qu = qs*us
	qv = qs*vs

	qu_1000_850 = 15000/2*(qu[TIME,5]+qu[TIME,4]) #1000 to 850
	qu_850_700 = 15000/2*(qu[TIME,4]+qu[TIME,3]) #850 to 700
	qu_700_500 = 20000/2*(qu[TIME,3]+qu[TIME,2]) #700 to 500
	qu_500_250 = 25000/2*(qu[TIME,2]+qu[TIME,1]) #500 to 250
	qu_250_100 = 15000/2*(qu[TIME,1]+qu[TIME,0]) #250 to 100

	qv_1000_850 = 15000/2*(qv[TIME,5]+qv[TIME,4]) #1000 to 850
	qv_850_700 = 15000/2*(qv[TIME,4]+qv[TIME,3]) #850 to 700
	qv_700_500 = 20000/2*(qv[TIME,3]+qv[TIME,2]) #700 to 500
	qv_500_250 = 25000/2*(qv[TIME,2]+qv[TIME,1]) #500 to 250
	qv_250_100 = 15000/2*(qv[TIME,1]+qv[TIME,0]) #250 to 100

	quog = (-1./9.81)*(qu_1000_850 + qu_850_700 + qu_700_500 + qu_500_250 + qu_250_100)
	qvog = (-1./9.81)*(qv_1000_850 + qv_850_700 + qv_700_500 + qv_500_250 + qv_250_100)

	IVT = (quog**2 + qvog**2)**0.5

	#plot ivt diagnostics
	m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,llcrnrlon=0,urcrnrlon=360,resolution='l')

	#ivtlevels = np.arange(900, 1100, 4)

	fig = plt.figure(figsize=(18.6, 10.5))
	ax = fig.add_axes((0,0,1,1))
	ax.set_axis_off()

	#m.drawcoastlines()

	# plot pres contours & low centers
	plt.contourf(lons, lats, IVT, linewidths=1, cmap='hot_r', zorder=0)
	plt.vector(lons, lats, quog, qvog)

	#plt.colorbar(fraction=0.025, pad=0.01)

	plt.savefig("/home/kalassak/ps-capstone/ivt_" + str(fnfmt(times[TIME])) + ".png", bbox_inches='tight', pad_inches=0, dpi=100)
	plt.close()

	print "plot for " + str(times[TIME]) + " generated"
