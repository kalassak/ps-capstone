import math
import netCDF4
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic

f = open('lowpts', 'r')
k = f.readlines()

m = Basemap(projection='cyl', llcrnrlat=-45,urcrnrlat=45,llcrnrlon=80,urcrnrlon=180,resolution='l')

fig = plt.figure(figsize=(18.6, 10.5))
ax = fig.add_axes((0,0,1,1))
ax.set_axis_off()

for line in k:
	data = line.strip('\n').split(',')
	ignoreflag = True
	if len(data) == 1:
		#set flags to skip plotting the first point of a track
		lastlat = False
		lastlon = False
		curname = data[0]
		annotated = False
		pass
	else:
		curlat = float(data[1])
		curlon = float(data[2])
		curwind = int(data[3])
		curflag = data[5]
		if lastlat != False and math.fabs(lastlon-curlon) > 180:
			#skip plotting one track point if it crosses the dateline
			lastlat = False
			lastlon = False
		if lastlat != False:
			if lastflag == 'False':
				c = '#ff0000'
			else:
				if lastwind < 34:
					c = '#007f00'
				elif lastwind < 64:
					c = '#00ff00'
				else:
					c = '#7fff7f'
				if annotated == False:
					#annotate first point in the track meeting TC criteria
					ax.annotate(curname, xy=(lastlon, lastlat), xytext=(3, -2), textcoords='offset points', color='k', zorder=1)
					print curname
					annotated = True
			m.plot([lastlon, curlon], [lastlat, curlat], color=c, linestyle='-', linewidth=1, zorder=0)
		lastlat = curlat
		lastlon = curlon
		lastwind = curwind
		lastflag = curflag
			
plt.savefig("/home/kalassak/ps-capstone/tracks_zoom.png", bbox_inches='tight', pad_inches=0, dpi=100)

plt.close()
