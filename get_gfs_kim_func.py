# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 00:04:54 2023

@author: Kimon
"""
import getgfs
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys
import re

def prepare_in(cords=[32.75,43.75,17.75,31],sres="0p25",pred_hrs=12):
    """
    Prepares the data needed to pul the GFS model.

    Parameters
    ----------
    cords : list, optional
        List of lat-long coordinate [Startlat,endlat,startlong,endlong]
        The box data shaped by these coordinates will be drawn. 
        The default is [32.75,43.75,17.75,31] Mapping the Greek general area.
    sres : string, optional
        Spacial resolution, between "0p25","0p50","1p00". The default is "0p25".
    pred_hrs : int, optional
        The amount of hours in the future to get predictions for. The default is 12.

    Returns
    -------
    pulldate : string
        The datetime string format needed to call GFS data.
    lat_str : string
        The latitude string format needed for to call GFS data.
    lon_str : string
        The longtitude string format needed for to call GFS data.
    lat : array
        The array containing latitude values to be pulled.
    lon : array
        The array containing longtitude values to be pulled.
    pdtxt : string
        The datetime string format needed for the txt save file.

    """
    #creates the string that are input into the get method in the get_data func
    lat_str='['+str(cords[0])+':'+str(cords[1])+']'
    lon_str='['+str(cords[2])+':'+str(cords[3])+']'
    #checks the resolution in order to create the step for the array used in the axis ticks on the plots
    if sres=="0p25":
        rd=0.25
    elif sres=="0p50":
        rd=0.5
    elif sres=="1p00":
        rd=1
    else:
        print('Error --- sres must be "0p25" or "0p50" or "1p00" --- process was cancelled')
        sys.exit(0)
    #arrrays containing the lat lon tick values
    lat=np.arange(cords[0],cords[1]+rd,rd)
    lon=np.arange(cords[2],cords[3]+rd,rd)
    #getting the curret datetime and adding the prediction hours
    new_datetime = datetime.now() + timedelta(hours=pred_hrs)
    #turning the datetime into the format read by the get method
    pulldate=str(new_datetime.year)
    #turning the datetime into the format for the txt title
    pdtxt=''
    
    if int(new_datetime.month)<10:
        pulldate+='0'+str(new_datetime.month)
    else:
        pulldate+=str(new_datetime.month)
    if int(new_datetime.day)<10:
        pulldate+='0'+str(new_datetime.day)
    else:
        pulldate+=str(new_datetime.day)
    pdtxt+=pulldate+" "
    pulldate+=" "+str(new_datetime.hour)+":00"
    if int(new_datetime.hour)<10:
        pdtxt+='0'
    pdtxt+=str(new_datetime.hour)+"00"
    return pulldate,lat_str,lon_str,lat,lon,pdtxt


def download_data(pulldate,parameters=["acpcpsfc","cpratavesfc","rhprs","hgtprs","tmp2m","tmpprs","ugrdprs","vgrdprs","tcdcprs","vissfc","cape255_0mb"],sres="0p25",tres_high=True,lat_str='[32.75:43.75]',long_str='[17.75:31]'):
    """
    Downloads the data from GFS for all parameters for the selected datetime.

    Parameters
    ----------
    pulldate : string
        The datetime string format needed for to call GFS data.
    parameters : list, optional
        list of strings containing the parameter names to be pulled. 
        The default is ["acpcpsfc","cpratavesfc","rhprs","hgtprs","tmp2m",
                        "tmpprs","ugrdprs","vgrdprs","tcdcprs","vissfc",
                        "cape255_0mb"].
    sres : string, optional
        Spacial resolution, between "0p25","0p50","1p00". The default is "0p25".
    tres_high : Boolean, optional
        if sres="0p25", a higher resolution option is available . The default is True.
    lat_str : string, optional
        The array containing latitude values to be pulled. The default is '[32.75:43.75]'.
    long_str : string, optional
        The array containing longtitude values to be pulled. The default is '[17.75:31]'.

    Returns
    -------
    gfs : getgfs.getgfs.Forecast
        The GFS forecast variable containing general info.
    res : getgfs.decode.File
        The GFS file continaining the numerical results.

    """
    if tres_high==True:
        if sres=="0p25":
            gfs=getgfs.Forecast(sres,'1hr')
        else:
            print("Error --- hourly data is only available for sres='0p25' --- process was cancelled")
    elif tres_high==False:
        gfs=getgfs.Forecast(sres)
    else:

        print('Error --- tres_high must be Boolean --- process was cancelled')
        sys.exit(0)
    
    print('Prediction time: '+pulldate)
    res=gfs.get(parameters,pulldate, lat_str,long_str)
    return gfs,res
   

def closest_num_idx(num,lst):
    """
    For a number find the closest number from a list.

    Parameters
    ----------
    num : float
        Number to find a close value to.
    lst : list 
        list of numbers.

    Returns
    -------
    closest_mb_index : float
        The closest number to num from the list given.

    """
    lst=np.array(lst)
    closest_mb_index = np.abs(lst - num).argmin()
    return closest_mb_index

def get_data(gfs,res,par,mb=False,fltr=True):
    """
    Gets the specific data for the parameter of interest from the gfs file

    Parameters
    ----------
    gfs : getgfs.getgfs.Forecast
        The GFS forecast variable containing general info.
    res : getgfs.decode.File
        The GFS file continaining the numerical results.
    par : str
        The name of the parameter of interest.
    mb : float, optional
        Height of prediction. The default is False.
    fltr : Boolean, optional
        If True it filters the prediction values based on the database fill value. 
        The default is True.

    Returns
    -------
    rt : array
        2D array containing the prediction values.

    """
    if par=='tcdcprs':
        #for cloud coverage
        mbl=[50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,925,950,975,1000]
        if isinstance(mb, (int, float)):
            level=closest_num_idx(mb,mbl)
            print("Data returned has the closest mb value equal to: "+str(mbl[level]))
            rt=res.variables[par].data[0][level]
        elif mb==False:
            print("No mb value was given for a mutlidimentional parameter, retirning the data with the lowest mb value")
            level=0
            rt=res.variables[par].data[0][level]
        else:
            print("Error----Invalid mb value. mb is numerical or left unassigned.")
            sys.exit(0)

    elif par in ["rhprs","hgtprs","tmpprs","ugrdprs","vgrdprs"]:
        #for rest multi dimentional
        mbl=[0.01,0.02,0.04,0.07,0.1,0.2,0.4,0.7,1,2,3,5,7,10,15,20,30,40,50,70,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,925,950,975,1000]
        if isinstance(mb, (int, float)):
            level=closest_num_idx(mb,mbl)
            print("Data returned has the closest mb value equal to: "+str(mbl[level]))
            rt=res.variables[par].data[0][level]
        elif mb==False:
            print("No mb value was given for a mutlidimentional parameter, retirning the data with the lowest mb value")
            level=0
            rt=res.variables[par].data[0][level]
        else:
            print("Error----Invalid mb value. mb is numerical or left unassigned.")
            sys.exit(0)
    elif par in ["acpcpsfc","cpratavesfc","tmp2m","vissfc","cape255_0mb"]:
        
        if mb==False:
            rt=res.variables[par].data[0]
        if mb!=False:
            print("Parameter given has no dimentionality. mb parameter was ignored")
            rt=res.variables[par].data[0]
    else:
        print("Error----Uknown parameter. Parameter not in the list of available parameters")
        sys.exit(0)
    rt=np.array(rt)
    if fltr==True:
        fval=gfs.variables[par]['missing_value']
        print("Filtering initiated on values equal to "+str(fval)+" acording to the GFS descriptions")
        mask = (rt == fval)
        rt[mask] = np.nan
    elif fltr==False:
        print("Acording to the GFS descriptions missing values are substituded with "+str(fval)+". For automatic filtering: fltr=True")
    else:
        print('Error---fltr parameter must be Boolean')
        sys.exit(0)
    return rt

def get_long_name(gfs,par):
    """
    Returns the long name format of the parameter from the GFS Database

    Parameters
    ----------
    gfs : getgfs.getgfs.Forecast
        The GFS forecast variable containing general info.
    par : str
        The name of the parameter of interest.

    Returns
    -------
    lname : str
        The long name of the parameter in the GFS database.

    """
    
    
    # Define the string (filtering out the '**' at the start)
    s = gfs.variables[par]['long_name'][2:]
    
    # Define the regex pattern : match any string that is inside parentheses or any non-whitespace characters.
    pattern = r"\(.*?\)\s*|\S+"
    
    # Use re.findall() to find all matches
    matches1 = re.findall(pattern, s)
    
    # Filter out the matches that contain '..'
    matches1 = [match for match in matches1 if '..' not in match]
    
    lname=""
    # Print the matches
    for match in matches1:
        lname+=match+" "
    return lname

def save_as_txt(f,file_name,path,columns):
    """Arguments
    --------------------
    f: array of data to save
    filen_name: string title for file (without the .txt)
    path: string path to save the outputs
    columns: list of stringscontaining the names of the columns 
    
    This function saves your dataset to a txt for easy access later.
    DO NOT USE / * . " / \ [ ] : ; | ,"""
    file=open(path+str(file_name)+'.txt','w')
    headline=''
    for col in columns:
        headline+=col+'\t'
    headline+='\n'
    file.write(headline)
    val=""
    if f.ndim!=1:
        for i in range(f.shape[0]):
            for j in range(f.shape[1]):
                val+=str(f[i,j])
                if j==f.shape[1]-1:
                    val+='\n'
                else:
                    val+='\t'
            file.write(val)
            val=""
    else:
        for i in f:
            val=str(i)+'\n'
            file.write(val)
    file.close()
    