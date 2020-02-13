import math
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import Basemap, addcyclic
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch

SEARCH = 5

def findNearestCell(lat, lon):
	x = (lon+180)*241/360
	y = (lat+90)*120/180
	return (int(x-1), int(y-1))

def getDisplacement(argmin):
	dx = argmin%7-3
	dy = argmin//7-3
	return (dx, dy)

def pad(n):
	if n < 10:
		n = "0%s" % n
	return n

def fnfmt(n):
	h = pad(int((n % 1)*24))
	d = pad(int(math.floor(n)))
	s = "%s_%s" % (d, h)
	return s

def flat(lat):
	if math.fabs(lat) < 10:
		zeroes = "0"
	else:
		zeroes = ""
	if lat > 0:
		return "%s%.1fN" % (zeroes, math.fabs(lat))
	else:
		return "%s%.1fS" % (zeroes, math.fabs(lat))

def flon(lon):
	if math.fabs(lon) < 10:
		zeroes = "00"
	elif math.fabs(lon) < 100:
		zeroes = "0"
	else:
		zeroes = ""
	if lon > 0:
		return "%s%.1fE" % (zeroes, math.fabs(lon))
	else:
		return "%s%.1fW" % (zeroes, math.fabs(lon))
		
def crop(arr):
	if j < SEARCH:
		eastarr = arr[-1,i-SEARCH:i+SEARCH+1,0:j+SEARCH+1]
		colstoadd = SEARCH-j
		westarr = arr[-1,i-SEARCH:i+SEARCH+1,nlons-colstoadd:]
		crop = np.concatenate((westarr, eastarr), axis=1)
	elif j >= nlons-SEARCH:
		colstoadd = SEARCH-(nlons-j)+1
		eastarr = arr[-1,i-SEARCH:i+SEARCH+1,0:colstoadd]
		crop = arr[-1,i-SEARCH:i+SEARCH+1,j-SEARCH:j+SEARCH+1]
		crop = np.concatenate((crop, eastarr), axis=1)
	else:
		crop = arr[-1,i-SEARCH:i+SEARCH+1,j-SEARCH:j+SEARCH+1]
	return crop

def calc_dist(lat1,lon1,lat2,lon2):
	R = 6371.0088
	lat1 = np.radians([lat1])
	lon1 = np.radians([lon1])
	lat2 = np.radians([lat2])
	lon2 = np.radians([lon2])

	dlat = lat2 - lat1
	dlon = lon2 - lon1
	a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2) **2
	c = 2 * np.arctan2(a**0.5, (1-a)**0.5)
	d = R * c
	return d

nc = netCDF4.Dataset("../nc/ncout.nc")

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]
pres = nc.variables['ps'][:]
us = nc.variables['ua'][:]*1.94384449 #to kt
vs = nc.variables['va'][:]*1.94384449
temps = nc.variables['ta'][:]

times = nc.variables['time'][:]

#pres = 0.01*psfc*np.exp(hgts/29.26/temps) #hypsometric equation and convert to hPa
winds = np.sqrt(us**2 + vs**2) #calc winds in kts

nc.close()

START_TIME = 30*4+0 #37 00
END_TIME = 40*4+0 #37 12
SURFACE_WIND_LEVEL = 5 #1000 hPa
UPPER_WIND_LEVEL = 1 #250 hPa
OUTFILE = "lowpts"
storms = {}
storm_id = 0

for TIME in xrange(START_TIME, END_TIME+1):
	# find low centers
	data_ext = minimum_filter(pres[TIME], 50, mode='nearest')
	mxy, mxx = np.where(data_ext == pres[TIME])

	# get lat/lon of all low centers
	low_lons = lons[mxx]
	low_lats = lats[mxy]

	# find wind maxima
	data_ext = maximum_filter(winds[TIME,SURFACE_WIND_LEVEL], 50, mode='nearest')
	mwy, mwx = np.where(data_ext == winds[TIME,SURFACE_WIND_LEVEL])

	# get lat/lon of all wind maxima
	wind_lons = lons[mwx]
	wind_lats = lats[mwy]

	#get info on each low
	CROP = 8
	print pres.shape
	min_prs = pres[TIME,mxy,mxx]

	#print info
	for low_lon, low_lat, y, x, min_pr in zip(low_lons, low_lats, mxy, mxx, min_prs):
		miny = y-CROP
		maxy = y+CROP
		minx = x-CROP
		maxx = x+CROP
		if miny < 0:
			miny = 0
		if maxy > 256:
			maxy = 256
		if minx < 0:
			minx = 0
		if maxx > 512:
			maxx = 512

		tropicalflag = True
		#criterion 2 - wind > 34 kt
		wind_grid = winds[TIME,SURFACE_WIND_LEVEL,miny:maxy,minx:maxx]

		wind = np.amax(wind_grid)
		if wind >= 34:
			wind_color = "\033[92m"
		else:
			wind_color = "\033[91m"
			tropicalflag = False

		#criterion 3 - 300 hPa wind < 20 m/s (average)
		upper_wind_grid = winds[TIME,UPPER_WIND_LEVEL,miny:maxy,minx:maxx]
		
		upper_wind = np.mean(upper_wind_grid)
		if upper_wind <= 38.8768898:
			upper_wind_color = "\033[92m"
		else:
			upper_wind_color = "\033[91m"
			tropicalflag = False

		#criterion 4 - convective precip > 0.36 mm/hr (average)
		#criterion 6 - 300 hPa wind < 8 m/s at track start (average)
		#criterion 8 - 300 hPa temp max in grid greater than average by 1 K
		upper_temp_grid = temps[TIME,UPPER_WIND_LEVEL,miny:maxy,minx:maxx]
		
		upper_temp_max = np.amax(upper_temp_grid)
		upper_temp_avg = np.mean(upper_temp_grid)
		upper_temp_anom = upper_temp_max - upper_temp_avg
		if upper_temp_anom > 1:
			upper_temp_anom_color = "\033[92m"
		else:
			upper_temp_anom_color = "\033[91m"
			tropicalflag = False

		print "%.1f %.1f (%s, %s)\t\t%s%d kts\033[0m %d hPa\t%s%d kts\033[0m\t%s%.1f K\033[0m" % (low_lat, low_lon, y, x, wind_color, wind, min_pr, upper_wind_color, upper_wind, upper_temp_anom_color, upper_temp_anom)

		#time,lat,lon,wind,pres ...
		#check if storm exists already in dictionary
		newstormflag = True
		stormdatatuple = (fnfmt(times[TIME]), low_lat, low_lon, wind, min_pr, tropicalflag)
		for storm in storms.items():
			if low_lat > 89.4 or low_lon == 0.0:
				#these boundaries are preferential locations for "artifact" storms
				#some real storms may be missed but they can be pieced together by visual assessment of the data
				newstormflag = False
				break
			if storm[1][-1][0] == fnfmt(times[TIME]):
				#do not try to match to storms which have already been updated to current time
				continue
			dist = calc_dist(storm[1][-1][1], storm[1][-1][2], low_lat, low_lon)
			if dist < 648: #within 648 km (moving at less than ~30 m/s)
				storm[1].append(stormdatatuple)
				newstormflag = False
				break

		if newstormflag == True:
			storms[storm_id] = [stormdatatuple]
			storm_id += 1

	#dump storms to file which have been inactive for 6 hr
	f = open(OUTFILE, 'a')
	for storm in storms.items():
		if storm[1][-1][0] == fnfmt(times[TIME]):
			pass
		else:
			f.write("%s\n" % storm[0])
			for stormdata in storm[1]:
				f.write("%s,%.1f,%.1f,%d,%d,%s\n" % stormdata)
			del storms[storm[0]]

	f.close()

	#plot low locations
	m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,llcrnrlon=0,urcrnrlon=360,resolution='l')

	preslevels = np.arange(900, 1100, 4)
	for i in xrange(0, 1): # remove this?
		fig = plt.figure(figsize=(18.6, 10.5))
		ax = fig.add_axes((0,0,1,1))
		ax.set_axis_off()

		#m.drawcoastlines()

		# plot pres contours & low centers
		plt.contour(lons, lats, pres[TIME], levels=preslevels, linewidths=1, colors='k', zorder=0)
		plt.plot(low_lons, low_lats, 'ro')
		plt.plot(wind_lons, wind_lats, 'yo')

		#plt.colorbar(fraction=0.025, pad=0.01)

		plt.savefig("/home/kalassak/ps-capstone/low_loc_" + str(fnfmt(times[TIME])) + ".png", bbox_inches='tight', pad_inches=0, dpi=100)
		plt.close()

		print "plot for " + str(times[TIME]) + " generated"
		i += 1

#dump all remaining storms to file
f = open(OUTFILE, 'a')
for storm in storms.items():
	f.write("%s\n" % storm[0])
	for stormdata in storm[1]:
		f.write("%s,%.1f,%.1f,%d,%d,%s\n" % stormdata)
	del storms[storm[0]]

f.close()
