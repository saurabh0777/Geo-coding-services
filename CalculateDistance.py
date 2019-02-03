#Sample code is used to calculate the distance between two Geo locations user can pass the file their file having lat and long and calculate the distance between the existing lat long

import pandas as pd
import numpy as np
import itertools
import math
import re
import geopandas as gpd
import rtree
import shapely
import fiona; fiona.supported_drivers

def caldist(old_site,va):
    var =int(va)
    # Specify the path of existing lat long
    new_site=pd.read_csv('Sites.csv')
    new_site= new_site.groupby('Area_Territory_Name')
    userfile = userfile_to_gpkg(old_site)
    userfile1= userfile.groupby('Area_Territory_Name')
    area = userfile.Area_Territory_Name.unique()[0]
    left = new_site.get_group(area)
    right = userfile1.get_group(area)
    sit2site_df = df_crossjoin(left,right).reset_index(drop=True)
    sit2site_df['Distance'] = sit2site_df.apply(lambda row: haversine((row['A_Latitude'], row['A_Longitude']), (row['Latitude'], row['Longitude'])),axis=1).reset_index(drop=True)
    sit2site_df.drop((sit2site_df[sit2site_df['Distance']>=var].index),inplace=True)
    for area in userfile.Area_Territory_Name.unique()[1:]:
        left = new_site.get_group(area)
        right = userfile1.get_group(area)
        sit2site_df = sit2site_df.append(df_crossjoin(left,right).reset_index(drop=True))
        sit2site_df['Distance'] = sit2site_df.apply(lambda row: haversine((row['A_Latitude'], row['A_Longitude']), (row['Latitude'], row['Longitude'])),axis=1).reset_index(drop=True)
    sit2site_df.drop((sit2site_df[sit2site_df['Distance']>=var].index),inplace=True)
    sit2site_df.to_csv('Finalresult.csv',index=False)
    final= pd.read_csv('Finalresult.csv')
    return final

# ------------------ User File change to GPKG and add Region  -------------------------------
def userfile_to_gpkg(usf):
    bace= gpd.read_file('ATMap_run.gpkg', index_col=False)
    crs = {'init':'epsg:4326'}
    bace= gpd.GeoDataFrame(bace,crs=crs)
    userfile= pd.read_csv(usf)
    geometry2 = [shapely.geometry.Point(xy) for xy in zip(userfile.Longitude, userfile.Latitude)]
    userfiletogpd=gpd.GeoDataFrame(userfile,crs=crs, geometry=geometry2)
    userfiletoreg=gpd.sjoin(userfiletogpd, bace, how='inner', op='intersects').reset_index(drop=True)
    userfiletoreg= userfiletoreg[['Latitude','Longitude','Area_Territory_Name','State']]
    userfiletoreg.to_csv('userfilefin.csv',encoding='utf8', index=False)
    us=pd.read_csv('userfilefin.csv')
    return us


def df_crossjoin(df1, df2, **kwargs):
    df1['_tmpkey'] = 1
    df2['_tmpkey'] = 1
    res = pd.merge(df1, df2, on='_tmpkey', **kwargs).drop('_tmpkey', axis=1)
    res.index = pd.MultiIndex.from_product((df1.index, df2.index))
    df1.drop('_tmpkey', axis=1, inplace=True)
    df2.drop('_tmpkey', axis=1, inplace=True)
    return res

def haversine(p1, p2):
    R = 6371.1    # earth radius in km
    p1 = [math.radians(v) for v in p1]
    p2 = [math.radians(v) for v in p2]

    d_lat = p2[0] - p1[0]
    d_lng = p2[1] - p1[1]
    a = math.pow(math.sin(d_lat / 2), 2) + math.cos(p1[0]) * math.cos(p2[0]) * math.pow(math.sin(d_lng / 2), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    #convert Result to Meters
    return R * c*1000
