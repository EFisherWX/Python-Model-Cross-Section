# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 23:05:45 2022

@author: evanw
"""

import numpy as np
import xarray as xr
from pyproj import Proj, transform
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from datetime import datetime

'''
I've yet to figure out how to overlay the map onto the upper-right corner of the cross
section. As such, you'll find the code necessary to build a map at the bottom of this script,
commented out in the same manner as this comment. All you'll need to do is comment out
everything between the '#HRRR grid' comment and the '#End cross section code' comment,
uncomment the map code, and run the script. This will generate a map displaying the
cross sectional path on a map given the start_coords and end_coords values.
'''

#---------- Assorted coordinates work ----------#


#Coordinates for start and end of cross section
#Cross section will be linear *in the HRRR's projected crs*
#This means it will appear slightly curved on a mercator map
start_coords = (35.7,-92.7)
end_coords = (35.1,-79.4)

#HRRR grid
x = np.arange(-2700573.2500000000000000,2696426.7500000000000000,3000)
y = np.arange(-1590306.1250000000000000,1586693.8750000000000000,3000)

#HRRR crs
kw_HRRR = dict(central_longitude=262.5, central_latitude=38.5, false_easting=0.0, false_northing=0.0, standard_parallels=(38.5,38.5))

#Convert start/end coordinates from lat/lon to projected
in_proj, out_proj = Proj(ccrs.PlateCarree()), Proj(ccrs.LambertConformal(**kw_HRRR))

#Execute transform of coordinates
proj_lon, proj_lat = transform(in_proj, out_proj, [start_coords[1],end_coords[1]], [start_coords[0],end_coords[0]])

#generate paths between starting and ending points in projected units
if proj_lon[0] > proj_lon[1]:
    proj_lon_path = np.arange(proj_lon[0],proj_lon[1],-3000)
else:
    proj_lon_path = np.arange(proj_lon[0],proj_lon[1],3000)
    
if proj_lat[0] > proj_lat[1]:   
    proj_lat_path = np.arange(proj_lat[0],proj_lat[1],-3000)
else:
    proj_lat_path = np.arange(proj_lat[0],proj_lat[1],3000)

#Adjust lengths of path arrays such that they are even
if len(proj_lon_path) < len(proj_lat_path):
    proj_lon_path = np.arange(min(proj_lon_path),max(proj_lon_path),(max(proj_lon_path)-min(proj_lon_path))/len(proj_lat_path))
elif len(proj_lat_path) < len(proj_lon_path):
    proj_lat_path = np.arange(min(proj_lat_path),max(proj_lat_path),(max(proj_lat_path)-min(proj_lat_path))/len(proj_lon_path))

#convert paths to indexes within HRRR coordinates
proj_lon_path_indexes = []
for a in proj_lon_path:
    proj_lon_path_indexes.append(min(range(len(x)), key=lambda i: abs(x[i]-a)))
    
proj_lat_path_indexes = []
for b in proj_lat_path:
    proj_lat_path_indexes.append(min(range(len(y)), key=lambda i: abs(y[i]-b)))
  
    
#---------- Collect data from file ----------#


#Open HRRR datafile, found here: https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/
#!-!-!-!-! You'll need to change the file path below to the location of your data
ds = xr.open_dataset('./HRRR Cross Section Data/hrrr.t12z.wrfnatf13.grib2',filter_by_keys={'typeOfLevel': 'hybrid'})

#Define lat/lon arrays along cross section path
lon = np.array(ds.t[0].longitude.data)[np.array(proj_lat_path_indexes),np.array(proj_lon_path_indexes)]
lat = np.array(ds.t[0].latitude.data)[np.array(proj_lat_path_indexes),np.array(proj_lon_path_indexes)]

#Define data arrays that will be used for plotting on cross section
x = []
for level in range(len(ds.t)):     
    x.append(np.arange(0,len(proj_lon_path_indexes),1))
    
y = np.log((np.array(ds.pres.data)[:,np.array(proj_lat_path_indexes),np.array(proj_lon_path_indexes)])/100)
z = (np.array(ds.t.data)[:,np.array(proj_lat_path_indexes),np.array(proj_lon_path_indexes)]-273.15)*(9/5)+32


#---------- Datetime work ----------#


dt_valid = datetime.strptime((str(ds.valid_time.data))[0:13],'%Y-%m-%dT%H')

dt_form_valid = dt_valid.strftime('%Hz %b %d, %Y')

dt_init = datetime.strptime((str(ds.time.data))[0:13],'%Y-%m-%dT%H')

dt_form_init = dt_init.strftime('%Hz %b %d, %Y')


#---------- Contourfs for temperature ----------#


#Initialize plot
fig, ax1 = plt.subplots(figsize=(10,5.625))

ax1.set_facecolor('#676668')
    
cmap = colors.LinearSegmentedColormap.from_list('custom blue', ['#FB68B3','#ED96CA','#D7B7D8','#9EDCE7','#27665B','#3E8070','#D3D3D3','#4A1E85','#7E1E4A','#CD7676','#F7E7E7','#7EB8D9','#6262A1','#FFFF78','#FD8F23','#B02A1B'], N=256)
bins = np.arange(-60,80.1,0.1)

cs = plt.contourf(x,y,z,bins,cmap=cmap,vmin=-60,vmax=80,zorder=0)


#---------- Contours for temperature ----------#


bins_cc = [-60,-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70]

cc = plt.contour(x,y,z,bins_cc,zorder=1,colors='#2e2e2e',linestyles='dashed',linewidths=0.5)

fmt = {}
for l, s in zip(cc.levels, bins_cc):
    fmt[l] = s

# Label every other level using strings
clb = ax1.clabel(cc, cc.levels, inline=True, fmt=fmt, fontsize=8, colors='#2e2e2e')


#---------- General plotting ----------#


cb=plt.colorbar(cs)

cb.set_ticks(np.arange(-60,81,10))
cb.set_ticklabels(['-60','-50','-40','-30','-20','-10','0','10','20','30','40','50','60','70','80'])

plt.gca().invert_yaxis()

#Trouble, assuming max lat and min lon occurs on left of plot
plt.xticks([0,max(x[-1])],[f'{round(start_coords[0],1)}N, {round(start_coords[1],1)}W',f'{round(end_coords[0],1)}N, {round(end_coords[1],1)}W'])
plt.yticks([np.log(1000),np.log(950),np.log(900),np.log(850),np.log(800),np.log(750),np.log(700),np.log(650),np.log(600),np.log(550),np.log(500),np.log(450),np.log(400),np.log(350),np.log(300),np.log(250),np.log(200),np.log(150),np.log(100),np.log(75),np.log(50),np.log(25),np.log(10)],['1000','','900','','800','','700','','600','','500','','400','','300','','200','','100','','50','','10'])

plt.ylim(np.log(1000),np.log(300))

plt.ylabel('Pressure (hPa)')

fig.text(0.13,0.89,'HRRR Cross Section, Temperature (fill, dashed contour, °F)')   
fig.text(0.13,0.92,f'Init: {dt_form_init}     Valid: {dt_form_valid}')

plt.savefig('./filename.png',bbox_inches='tight',dpi=200)
#End cross section code


'''
fig = plt.figure(figsize=(10, 5.625))

ax2 = plt.axes(projection=ccrs.LambertConformal())

ax2.add_feature(cfeature.STATES, linewidth=0.5)

#If you want counties on your map, you'll need your own shapefile and path. Otherwise the next line will throw an error.
reader = shpreader.Reader('./Shapefiles/cb_2018_us_county_5m.shp')
counties = list(reader.geometries())
COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
ax2.add_feature(COUNTIES, facecolor='none', linestyle=':', linewidth=0.3, zorder=0)

ROI = 'CONUS'
lon_min = min([start_coords[1],end_coords[1]])-2
lat_min = min([start_coords[0],end_coords[0]])-1
lon_max = max([start_coords[1],end_coords[1]])+2
lat_max = max([start_coords[0],end_coords[0]])+1

ax2.set_extent([lon_min, lon_max, lat_min, lat_max],ccrs.PlateCarree())

yy = [start_coords[0], end_coords[0]]
xx = [start_coords[1], end_coords[1]]

ax2.plot(xx,yy,transform=ccrs.PlateCarree(),color='red',linewidth=4,zorder=10)
ax2.scatter(xx,yy,transform=ccrs.PlateCarree(),c='red',s=300,zorder=10)

#plt.savefig('./filename-map.png',bbox_inches='tight',dpi=200)
'''