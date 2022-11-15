from bs4 import BeautifulSoup
import codecs
import datetime
from datetime import datetime
import json
import math
import numpy as np
import os
from random import random
import random
import re
import requests
import pandas as pd
import shutil
import statistics
from statistics import mean
import time
import unidecode
import urllib.request


from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from meta_pubs import list_affs


def write_geojson():
    """
    analyze data
    """

    print("running write_geojson")

    tasks = [1]

    if 1 in tasks: save_geojson()


    print("completed write_geojson")



def save_geojson():
    """
    for each aff or each pub
    create a line of geojson
    """

    features = []

    for fil in os.listdir(retrieve_path('crossref_json')):

        if 'compiled' in fil: continue
        if '_located' in fil: continue

        fil_src = os.path.join(retrieve_path('crossref_json'), fil)
        for pub in retrieve_json(fil_src)['results']:

            color = make_color()

            for aff in pub['affs']:

                found = retrieve_geolocated(aff)

                print('aff = ' + str(aff))

                print('found = ')
                print(found)


                geolocated = {}
                geolocated['lat'] = found['lat']
                geolocated['lon'] = found['lon']
                geolocated['display_name'] = found['display_name']
                geolocated['aff'] = aff
                geolocated['title'] = pub['title'][0]
                geolocated['url'] = pub['doi_url']
                geolocated['color'] = color
                geolocated['radius'] = 10 + 3*float(pub['is-referenced-by-count'])
                geolocated['opacity'] = 0.7
                geolocated['zindex'] = int(500 - geolocated['radius'])
                geolocated['paneName'] = 'pane_' + str(int(1000 - geolocated['radius']))
                #geolocated['journal'] = pub['container-title']

                feature = {}
                feature['type'] = 'Feature'
                feature['properties'] = make_prop(geolocated)
                feature['geometry'] = make_geo(geolocated)
                features.append(feature)


                geojson = {}
                geojson['type'] = 'FeatureCollection'
                geojson['features'] = features

                dst_json = os.path.join(retrieve_path('map_geojson'))
                #print('dst_json = ' + str(dst_json))
                with open(dst_json, "w") as f:
                    f.write('var ' + ' pubs' + ' = ')
                    json.dump(geojson, f, indent = 6)
                    f.write(';')
                f.close()


def retrieve_geolocated(aff):
    """
    return json for found
    """

    print('fil_src = ')
    print(retrieve_path('located_compiled'))

    aff = unidecode.unidecode(aff)

    for found in retrieve_json('located_compiled')['affs']:

        if found['name'] != aff: continue

        print('aff = ')
        print(aff)

        print('found = ')
        print(found)

        return(found)


def make_geo(geolocated):
    """
    return json for geometry
    """

    geo = {}
    geo['type'] = 'Point'
    geo['coordinates'] = [ float(geolocated['lon']), float(geolocated['lat'])]
    return(geo)


def make_prop(geolocated):
    """
    return json describing prop
    """
    prop = {}
    for key in geolocated.keys():
        prop[key] = geolocated[key]
    return(prop)



def make_color():
    """
    return a list of colors formatted as rgb
    according to the color type and scaled
    """

    norm = 255*random.random()
    print('norm = ' + str(norm))

    #norm = 255*(value_max - value)/(value_max - value_min)

    mods = [0.5, 0.5, 0.5]
    r = int(255 - 255*random.random()*mods[0])
    g = int(255 - 255*random.random()*mods[1])
    b = int(255 - 255*random.random()*mods[2])

    color_str = str('rgb( ' + str(r) + ' , ' +  str(g) + ' , ' + str(b) + ' )')
    return(color_str)
