# -*- coding: utf-8 -*-
import feedparser
import re
import time
from bs4 import BeautifulSoup as bs
from collections import namedtuple

import datetime
from sources import sources

News = namedtuple("News", "title description link date")

def custom_strip_tags(value):
    soup = bs(value);
    allFontTags = soup.find_all("font",{"size":"-1"});
    if(len(allFontTags) > 0):
        content = soup.find_all("font",{"size":"-1"})[1];
    else:
        content = value;    
    result = re.sub(r'<[^>]*?>', ' ', unicode(content))
    
    return unicode(result)

def get_sources():
    for i, (url, tag) in enumerate(sources.items()):
        if i > 1:
            break
        try:
            lenta = feedparser.parse(url)
            for entry in lenta.entries:
                structTime = entry.updated_parsed
                dt = datetime.datetime(*structTime[:6])
                #str_date = time.strftime('%d/%m/%Y %H:%M:%S',entry.updated_parsed)
                description = custom_strip_tags(entry.description)
                news = News(entry.title, description, entry.link, dt)
                yield tag, news
        except Exception as err:
            print err
            pass
