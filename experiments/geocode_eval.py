#-*- coding: UTF-8 -*-

import os
from math import cos, sin, radians
from argparse import ArgumentParser
import datetime as dt
import numpy as np
import pandas as pd
from pandas import DataFrame
import scipy.cluster.hierarchy as hcluster
import geocoder
import time
import cPickle as pickle




def handle_args():
    parser = ArgumentParser()
    parser.add_argument('-f', '--fname', default = 'Crisismap - all news.csv')
    parser.add_argument('-g', '--geocod', default = 'google')
    parser.add_argument('-n', '--number', default = 1000)
    parser.add_argument('--random', dest= 'random', action = 'store_true')
    parser.add_argument('--no-random', dest= 'random', action = 'store_false')
    parser.set_defaults(random=True)
    args = parser.parse_args()
    return args

#geocod = 'google'

coordinates = {} # get cached
toponyms = {} # get cached

#print coder ('Хакасия').geojson #.latlng
from ..toponyms.top import extract_toponyms



files = os.listdir(os.curdir)
if 'coordinates' in files:
    #with open ('coordinates', 'r') as file:
    with open ('new_brave_world/experiments/coordinates', 'r') as file:

        coordinates = pickle.load(file)
#ort dbm
#coordinates = dbm.open()

def geolocate(toponyms , geocod):
    coder = getattr(geocoder, geocod)
    locations = []
    for toponym in toponyms:
        #print toponym
        if toponym in coordinates.keys():
            location = coordinates[toponym]
        else:
            location = coder(toponym).geojson #.latlng
            #print location.geojson['properties']['status']
            #print 'going to bed...'
            if location['properties']['status'] == 'OVER_QUERY_LIMIT':
                print 'going to bed...'
                time.sleep(10)
                #print location.geojson['properties']['status']
                location = coder(toponym).geojson #.latlng

        #print toponym, location
            coordinates[toponym] = location
            #print location.geojson['properties']['status']
        #if not location.geojson['properties']['status'] == 'ZERO_RESULTS':
        if 'lat' in  location['properties'].keys() and 'lng' in location['properties'].keys():
            locations.append((location['properties']['lat'], location['properties']['lng']))
        else:
            print 'no coordinates', toponym, location['properties']['status']


    return locations

def main_point(points):
    if len(points) > 0:
        return points[-1]
    else:
        return ''

def lat(point):
    if len(point) > 0:
        return point[0]
    else:
        return ''

def long(point):
    if len(point) > 0:
        return point[1]
    else:
        return ''


def lotop(text):
    ts = tuple(extract_toponyms(text))

    return ts

def main():
    args = handle_args()
    fname = 'new_brave_world/experiments/' + args.fname
    geocod = args.geocod
    number = int(args.number)
    random = bool(args.random)
    print bool('False')
    print random

    #geocod = 'google'
    #fname = 'Crisismap - all news.csv'
    #random = False
    #number = 100
    df = pd.read_csv(fname, sep = ';', encoding = "utf8")
    if random:
        print 'permutation'
        df = df.ix[np.random.permutation(df.index)]
    df = df[:number]


    df["text"] = df.Title.map(unicode) + df.Description.map(unicode)
    #df.text.map(geolocate)
    df['toponyms'] = df.text.apply(lotop)
    #df['phrases'] = ','.join (df.toponyms)
    df['points'] = df.toponyms.apply(geolocate, args = (geocod,))
    df['point'] = df.points.apply(main_point)
    df['lat'] = df.point.apply(lat)
    df['long'] = df.point.apply(long)





    now = dt.datetime.now().isoformat().replace(":", "_")
    result_name = "_".join([os.path.splitext(fname)[0], now , "result.csv"])
    columns = ["toponyms", 'lat', 'long', 'points', "pub_date", "type", "text"]
    df[columns].to_csv(result_name, encoding = "utf8", sep = "\t", index = False)

    with open ('coordinates', 'w') as file:
        pickle.dump(coordinates, file)

if __name__ == "__main__":
    main()
