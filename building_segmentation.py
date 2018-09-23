#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 12:43:57 2018

@author: dutchman
"""
import requests
import yaml
import numpy as np
from numba import jit
import imageio
import matplotlib.pyplot as plt

YMLFILE = open("config.yml", 'r')
CFG = yaml.load(YMLFILE)

def get_url(lat, lon, cfg):
    """
    Create url to use for downloading an image from google.

    Parameters
    ----------
    lat : float
    lon : float
    cfg : dict, from config.yml
    """
    url = "https://maps.googleapis.com/maps/api/staticmap?key=" + cfg['api_key']
    url += "&center=%f,%f&zoom=%d" % (lat, lon, cfg['zoom'])
    url += "&format=%s&maptype=%s" % (cfg['format'], cfg['maptype'])
    url += "&style=element:labels%7Cvisibility:off"
    url += "&style=feature:administrative.land_parcel%7C"
    url += "visibility:off&style=feature:administrative.neighborhood%7C"
    url += "visibility:off&style=feature:landscape.man_made%7C"
    url += "element:geometry.fill%7Csaturation:10%7Clightness:-20%7C"
    url += "visibility:on%7Cweight:8&"
    url += "size=%s" %(cfg['size'])

    return url

@jit
def segment_buildings(img, color_list):
    """
    Use mapstyle segmentation to split image into building/not building.

    Parameters
    ----------
    img : np.array
    color_list : dict of lists
    """
    retval = img.copy()
    w, h, d = retval.shape
    for x in range(w):
        for y in range(h):
            newval = np.array([0, 0, 0])
            for ctype in color_list:
                if np.equal(retval[x, y][:3], color_list[ctype]).all():
                    newval = np.array([255, 255, 255])
                    break
            retval[x, y][:3] = newval

    return retval


def download_map_segment(outname, lat, lon):
    """
    Parameters
    ----------
    outname : string
    lat : float
    lon : float
    """
    url2 = get_url(lat, lon, CFG)

    print(url2)

    f = open(outname,'wb')
    f.write(requests.get(url2).content)
    f.close()

    img = imageio.imread(outname)
    #plt.imshow(img)
    #plt.imshow(segment_buildings(img, CFG['building_colors']))
    plt.imshow(segment_buildings(img, CFG['shanghai_colors']))
    plt.show()



if __name__ == '__main__':
    LAT = 47.999
    LON = 7.8421
    LAT, LON = 31.212801, 121.452318
    download_map_segment('example.png', LAT, LON)
