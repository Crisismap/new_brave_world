#-*- coding: UTF-8 -*-

import os
from argparse import ArgumentParser
import datetime as dt
import numpy as np
import pandas as pd
import geocoder
import time
import cPickle as pickle


def handle_args():
    parser = ArgumentParser()
    parser.add_argument('-f', '--fname', default='crisismap_with_toponyms.csv')
    parser.add_argument('-g', '--geocod', default='google')
    parser.add_argument('-n', '--number', default=1000, type=int)
    parser.add_argument('--random', dest='random',
                        action='store_true', default=True)
    parser.add_argument('--no-random', dest= 'random', action = 'store_false')
    parser.set_defaults(random=True)
    args = parser.parse_args()
    return args


def geolocate(s, geocod, coordinates):
    coder = getattr(geocoder, geocod)
    locations = []
    toponyms = s.split(', ')
    for toponym in toponyms:
        #print toponym
        if toponym in coordinates.keys():
            location = coordinates[toponym]
        else:

            location = coder(toponym).geojson
            if location['properties']['status'] == 'OVER_QUERY_LIMIT':
                print 'im going to bed...'
                time.sleep(10)
                location = coder(toponym).geojson

            coordinates[toponym] = location
        if 'lat' in location['properties'].keys() and 'lng' in location['properties'].keys():
            locations.append(
                (location['properties']['lat'], location['properties']['lng']))
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


#def lotop(text):
#    from ..toponyms.top import extract_toponyms
#    ts = tuple(extract_toponyms(text))

    #return ts


def main():
    args = handle_args()
    #fname = 'new_brave_world/experiments/' + args.fname
    fname = args.fname

    geocod = args.geocod
    number = args.number
    random = args.random

    #files = os.listdir(os.path.join(os.curdir, 'new_brave_world/experiments'))
    files = os.listdir(os.curdir)
    if 'coordinates' in files:
        with open('coordinates', 'r') as file:
            coordinates = pickle.load(file)
    else:
        coordinates = {}

    df = pd.read_csv(fname, sep='\t', encoding="utf8")
    if random:
        print 'permutation'
        df = df.ix[np.random.permutation(df.index)]
    df = df[:number]

    df["text"] = df.Title.map(unicode) + df.Description.map(unicode)
    #df['toponyms'] = df.text.apply(lotop)
    df['points'] = df.toponyms.apply(geolocate, args=(geocod,coordinates))
    df['point'] = df.points.apply(main_point)
    df['lat'] = df.point.apply(lat)
    df['long'] = df.point.apply(long)

    now = dt.datetime.now().isoformat().replace(":", "_")
    result_name = "_".join([now, "result.csv"])
    columns = ["toponyms", 'lat', 'long', 'Title', "Description", 'points']
    df[columns].to_csv(result_name, encoding="utf8", sep="\t", index=False)

    with open('coordinates', 'w') as file:
        pickle.dump(coordinates, file)


if __name__ == '__main__':
    main()
