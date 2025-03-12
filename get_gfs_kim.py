# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 18:11:37 2023

@author: Kimon
"""

import getgfs
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys
import re
from get_gfs_kim_func import *
print("Current datetime: "+str(datetime.now()))


parameters=["acpcpsfc","cpratavesfc","rhprs","hgtprs","tmp2m","tmpprs","ugrdprs","vgrdprs","tcdcprs","vissfc","cape255_0mb"]
cords=[32.75,43.75,17.75,31]
sres="0p25"
pred_hrs=12
tres_high=True


#setting up the data
pulldate,lat_str,lon_str,lat,lon,pdtxt=prepare_in(cords,sres,pred_hrs)
#pulling the data
gfs,res=download_data(pulldate=pulldate,tres_high=tres_high)

#%%
for p in parameters:
    lname=get_long_name(gfs, p)
    print(p+":"+lname)

#%% Select a parameter

#selecting a parameter
par='tcdcprs'
mb=200

#getting the parameter's original name from the database
lname=get_long_name(gfs, par)
print('Parameter selected: '+par+'( '+lname+')')

#separating the specific parameter,selecting mb value and filtering missing values
rt=get_data(gfs,res,par,mb,fltr=True)

#%%
#plotting   
plt.imshow(rt,cmap='jet',origin='lower')
cb=plt.colorbar()
cb.ax.set_ylabel(lname, rotation=270,labelpad=15)
# Set the x-axis labels
plt.xticks(np.arange(len(lon)), lon)

# Set the y-axis labels
plt.yticks(np.arange(len(lat)), lat)
# Reduce the number of ticks
ax = plt.gca()
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.title('datetime: '+pulldate)
