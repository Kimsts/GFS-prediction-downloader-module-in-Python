# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 18:11:37 2023

@author: Kimon
"""

import getgfs
from datetime import datetime, timedelta
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
import sys
import re
from get_gfs_kim_func import *
print("Current datetime: "+str(datetime.now()))
#%%

parameters=["acpcpsfc","cpratavesfc","rhprs","hgtprs","tmp2m","tmpprs","ugrdprs","vgrdprs","tcdcprs","vissfc","cape255_0mb"]
cords=[32.75,43.75,17.75,31]
sres="0p25"
pred_hrs=12
tres_high=True
path=r'C:\Users\Kimon\Downloads\\'

parm=["rhprs","hgtprs","tmpprs","ugrdprs","vgrdprs","tcdcprs"]
mb= [100, 200 ,300, 400, 500, 600, 700, 750, 800, 850, 900, 950, 1000]

#%%
#setting up the data
pulldate,lat_str,lon_str,lat,lon,pdtxt=prepare_in(cords,sres,pred_hrs)
#pulling the data
gfs,res=download_data(pulldate=pulldate,tres_high=tres_high)


cols=["lat","lon"]

for i in mb:
    cols.append(str(i)+"mbl")
#%%
for par in parm:
    #getting the parameter's original name from the database
    lname=get_long_name(gfs, par)
    print('Parameter selected: '+par+'( '+lname+')')
    if par in ["rhprs","hgtprs","tmpprs","ugrdprs","vgrdprs","tcdcprs"]:
        matrix=np.empty((len(lat)*len(lon),2+len(mb)))
        e=0
        for i in range(len(lat)):
            for j in range(len(lon)):
                matrix[e,0]=lat[i] 
                matrix[e,1]=lon[j]
                e+=1
        k=0
        for l in mb:
            
            #separating the specific parameter,selecting mb value and filtering missing values
            rt=get_data(gfs,res,par,l,fltr=True)
            
            e=0
            for i in range(rt.shape[0]):
                for j in range(rt.shape[1]):
                    matrix[e,2+k]=rt[i,j]
                    e+=1
            k+=1
        save_as_txt(matrix,pdtxt+" "+par,path,cols)
    if par in ["acpcpsfc","cpratavesfc","tmp2m","vissfc","cape255_0mb"]:
        matrix=np.empty((len(lat)*len(lon),3))
        #separating the specific parameter,selecting mb value and filtering missing values
        rt=get_data(gfs,res,par,False,fltr=True)
        
        
        e=0
        
        for i in range(rt.shape[0]):
            for j in range(rt.shape[1]):
                matrix[e,0]=lat[i] 
                matrix[e,1]=lon[j]
                matrix[e,2]=rt[i,j]
                e+=1
                
        save_as_txt(matrix,pdtxt+" "+par,path,["lat","lon",par])
    

   