import math
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic

f = open('lowpts', 'r')
k = f.readlines()

#create 1x1 deg bins to store tc track activity and cyclogenesis 'heat'
BINSIZE = 2
activity_bins = np.zeros((360/BINSIZE, 180/BINSIZE))
cyclogenesis_bins = np.zeros((360/BINSIZE, 180/BINSIZE))
curstorm_bins = np.zeros((360/BINSIZE, 180/BINSIZE))

print "generating TC heatmaps with bin size %d" % BINSIZE

for line in k:
	data = line.strip('\n').split(',')
	if len(data) == 1:
		#set flags to skip plotting the first point of a track
		lastlat = False
		lastlon = False
		curname = data[0]
		formed = False
		curstorm_bins[:] = 0
		pass
	else:
		curlat = float(data[1])
		curlon = float(data[2])
		curwind = int(data[3])
		curflag = data[5]
		
		#calculate bin
		lonbin = int(math.floor(curlon/BINSIZE)) #if lon is 40 put in bin 40
		latbin = 90/BINSIZE-int(math.floor(curlat/BINSIZE)) #if lat is 40 put in bin 50, -40 in 130

		#if this point is tropical
		if curflag == 'True': 
			#if this is the first tropical point or the cyclone regenerates
			if formed == False: #or lastflag == 'False'
				cyclogenesis_bins[lonbin,latbin] += 1 #add tc genesis point to cyclogenesis_bins
				formed = True
			#if this storm has already been in this bin don't count it again
			if curstorm_bins[lonbin, latbin] < 1:
				activity_bins[lonbin,latbin] += 1 #add tc point to activity_bins

			#make a note that tc has been in this lat/lon bin
			curstorm_bins[lonbin, latbin] += 1

		lastlat = curlat
		lastlon = curlon
		lastwind = curwind
		lastflag = curflag

#plot total activity bins
m = Basemap(projection='cyl', llcrnrlat=-45,urcrnrlat=45,llcrnrlon=80,urcrnrlon=180,resolution='l')

fig = plt.figure(figsize=(18.6, 10.5))
ax = fig.add_axes((0,0,1,1))
ax.set_axis_off()

lons, lats = np.meshgrid(np.linspace(0., 360., 360/BINSIZE+1), np.linspace(90., -90., 180/BINSIZE+1))

m.pcolormesh(lons, lats, np.swapaxes(activity_bins, 0, 1), cmap='hot_r', zorder=0)

plt.colorbar(fraction=0.025, pad=0.01)
			
plt.savefig("/home/kalassak/ps-capstone/heatmap_activity_zoom.png", bbox_inches='tight', pad_inches=0, dpi=100)

plt.close()

#plot cyclogenesis bins
m = Basemap(projection='cyl', llcrnrlat=-45,urcrnrlat=45,llcrnrlon=80,urcrnrlon=180,resolution='l')

fig = plt.figure(figsize=(18.6, 10.5))
ax = fig.add_axes((0,0,1,1))
ax.set_axis_off()

lons, lats = np.meshgrid(np.linspace(0., 360., 360/BINSIZE+1), np.linspace(90., -90., 180/BINSIZE+1))

m.pcolormesh(lons, lats, np.swapaxes(cyclogenesis_bins, 0, 1), cmap='hot_r', zorder=0)

plt.colorbar(fraction=0.025, pad=0.01)
			
plt.savefig("/home/kalassak/ps-capstone/heatmap_cyclogenesis_zoom.png", bbox_inches='tight', pad_inches=0, dpi=100)

plt.close()
