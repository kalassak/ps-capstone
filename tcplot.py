import netCDF4
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic

f = open('lowpts', 'r')
k = f.readlines()

m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,llcrnrlon=0,urcrnrlon=360,resolution='l')

fig = plt.figure(figsize=(18.6, 10.5))
ax = fig.add_axes((0,0,1,1))
ax.set_axis_off()

for line in k:
	data = line.strip('\n').split(',')
	ignoreflag = True
	if len(data) == 1:
		lastlat = False
		lastlon = False
		pass
	else:
		curlat = data[1]
		curlon = data[2]
		curflag = data[5]
		if lastlat != False:
			if curflag == 'False':
				c = '#ff0000'
			else:
				c = '#00ff00'
			plt.plot([lastlon, curlon], [lastlat, curlat], color=c, linestyle='-', linewidth=1, zorder=0)
		lastlat = curlat
		lastlon = curlon
			
plt.savefig("/home/kalassak/ps-capstone/tracks.png", bbox_inches='tight', pad_inches=0, dpi=100)

plt.close()
