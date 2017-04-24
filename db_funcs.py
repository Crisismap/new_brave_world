# -*- coding: utf-8 -*-
import geocoder
import json
import hashlib
import logging
import sys
import unicodedata

from app import db
from db_models import *

from toponyms.top import * #extract_toponyms

def hash(string):
    return hashlib.sha1(string.encode('utf8')).hexdigest()

#the function is limited by number of items returned by get_sources
def insert_data(limit = 5):
    from get_sources import get_sources
    for tag, news in get_sources(limit = limit):
        tag_obj = Tag.query.filter_by(name = tag).first()
        if tag_obj is None:
            tag_obj = Tag(tag)
            db.session.add(tag_obj)
        h = hash(news.description)
        if not News.query.filter_by(id = h).all():
            n = News(title = news.title,
                    description = news.description,
                    link = news.link,
                    tag = tag_obj,
                    hash = h)
            logging.debug(n.txt)
            db.session.add(n)
    db.session.commit()

#mock function, to be replaced by a real one 
#def extract_toponyms(news):
#    #translation table for removing punctuation
#    for word in news.split():
#          if word[0].isupper():
#             yield  word.translate(tbl)




def add_toponyms():
    for n in News.query.filter_by(toponyms_added = False):
        for toponym in extract_toponyms(n.title + n.description):
            toponym_obj = Toponyms.query.filter_by(name = toponym).first()
            if toponym_obj is None:
                toponym_obj = Toponyms(toponym)
                db.session.add(toponym_obj)
            n.toponyms.append( toponym_obj)
        n.toponyms_added = True
    db.session.commit()
        
def geocode_toponyms():
    for t in Toponyms.query.filter_by(loc = None).limit(2000):
        logging.debug(t.name)
        result = geocoder.osm(t.name)
        box = json.dumps(result.bbox)
        geojson = json.dumps(result.geojson, ensure_ascii= False)
        loc_obj = Localization.query.filter_by(box = box).first()
        if loc_obj is None:
            loc_obj = Localization(box, geojson)
            db.session.add(loc_obj)
        t.loc =  loc_obj
    db.session.commit()

def get_coords(loc):
    if loc:
        geojson = json.loads(loc.geojson)
        coords = geojson.get("geometry", {}).get("coordinates")
        if coords:
            return coords[::-1]

def get_country(loc):
    if loc:
        geojson = json.loads(loc.geojson)
        country= geojson.get("properties", {}).get("country")
        return country


def add_locs():
    our_countries = {u"Україна", u'Россия'}
    #for n in News.query.filter_by(localization_added = False):
    for n in News.query.all():
        for toponym in n.toponyms:
                loc = toponym.loc
                if loc:
                    coords = get_coords(loc)
                    country = get_country(loc)
                    if coords and country in our_countries:
                        n.loc = loc
                        break
    n.localization_added = True
    db.session.commit()
 


def check_geocoding():
    i = 0
    our_countries = {u"Україна", u'Россия'}
    countries = []
    for t in Toponyms.query.all():
        if t.loc is not None:

            #print i
            #print t.name
            #print t.loc.box
            #print t.loc.geojson
            geojson = json.loads(t.loc.geojson)
            country= geojson.get("properties", {}).get("country")
            countries.append(country)
            coords= geojson.get("geometry", {}).get("coordinates")
            if country in our_countries:
                print  i
                print  t.name
            i +=1
    #for c in set( countries):
    #    print c

def check_toponyms():
    for n in News.query.filter_by(toponyms_added = True):
            print n.txt
            for elem in n.toponyms:
                print elem.name
    for t in Toponyms.query.all():
            print t.name


