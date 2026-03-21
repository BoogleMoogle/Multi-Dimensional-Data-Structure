from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np
import os
#to see stack
import inspect








####################### GENERAL METHODS #######################
def points_from_file(path=None,columns=None,file_extension=None,drop_duplicates=False,gowala=False,limit=1000):        #Need to make it where it can split the csv file with delimeter = ' ' or ','. Also make method to work with .txt
    if path == None:
        return print("Need path!")
    
    if gowala==True:
        if limit == False or limit == None:
            points = pd.read_csv(path,sep='\t',header=None,usecols=columns,names=['timestamp','Lat','Long'])
        else:
            points = pd.read_csv(path,sep='\t',header=None,usecols=columns,names=['timestamp','Lat','Long'],nrows=limit)
        points = points.dropna()
        points['timestamp'] = pd.to_datetime(points['timestamp'],format="%Y-%m-%dT%H:%M:%SZ")
        #make time stamp into seconds
        points['timestamp'] = (points['timestamp'] - pd.Timestamp("2009-02-01")).dt.total_seconds().astype(int)
    elif file_extension == 'csv':
        points = pd.read_csv(path)
        # points = points.dropna(how='any')
    elif file_extension == 'excel':
        points = pd.read_excel(path)
    else:
        points = pd.read_csv(path)
        # points = points.dropna(how='any')

    if columns != None:
        if gowala != True:
            points = points[columns]
            if file_extension=='csv':
                points = points.dropna()

    if drop_duplicates == True:
        points = points.drop_duplicates()

    points = points.values.tolist()
    return points

##############################################################













##### DATASETS #####
    #All /SHOULD/ automatically be set to drop duplicates

# ### CRAWDAD spitz/cellular Dataset Dropping Duplicates ###
# path = r"Saved Datasets/DT-mobile-data.csv/VDS_MS_310809_27_0210.csv"
# points = points_from_file(path,columns=['Laenge','Breite'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#


# ### SRFG-v1 ###
# path = r"Saved Datasets/Check/SRFG-v1.csv"
# points = points_from_file(path,columns=['lat','long'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#

# ### Inventory of Owned & Leased Properties (IOLP) ###
# building_path = r"Saved Datasets/Inventory of Owned and Leased Properties/2026-2-20-iolp-buildings.xlsx"
# lease_path = r"Saved Datasets/Inventory of Owned and Leased Properties/2026-2-20-iolp-leases.xlsx"

# points = points_from_file(lease_path,columns=['Latitude','Longitude'],file_extension='excel',drop_duplicates=True)
# building_points = points_from_file(building_path,columns=['Latitude','Longitude'],file_extension='excel',drop_duplicates=True)
# #_____________________________________________________________________________#


# ### Spatial Database NO Duplication ###
# path = r"Saved Datasets/Spatial.xlsx"
# points = points_from_file(path,columns=['lon','lat'],file_extension='excel',drop_duplicates=True)
# #___________________________________________________________________________#


# ### House ###
# path = r"Saved Datasets/house_data.csv"
# points = points_from_file(path,columns=['price','bedrooms','sqft_living'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#


### Gowala ###      social netowrk
path = r"Saved Datasets/Gowalla_totalCheckins.txt"
points = points_from_file(path,columns=[1,2,3],file_extension='csv',drop_duplicates=True,gowala=True,limit=1000)
#___________________________________________________________________________#


### Template for SRC path and BRC path ###
# SRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/"
# BRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/"













# class KSTree:
#     def __init__(self,points=[],depth=0,axis=0,split_value=None,bbox=[],children=[],parent=[],cuttof=1):


















