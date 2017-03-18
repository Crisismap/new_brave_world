# -*- coding: utf-8 -*-
import feedparser
import re
import time
from bs4 import BeautifulSoup

import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sources import sources


def custom_strip_tags(value):
    soup = BeautifulSoup(value);
    allFontTags = soup.find_all("font",{"size":"-1"});
    if(len(allFontTags) > 0):
        content = soup.find_all("font",{"size":"-1"})[1];
    else:
        content = value;    
    result = re.sub(r'<[^>]*?>', ' ', unicode(content))
    
    return unicode(result)


class News():
    __tablename__ = "news"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    description = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)



def get_sources():
    for i, url in enumerate(sources.keys()):
        if i > 1:
            break
        try:
            lenta = feedparser.parse(url);
            for entry in lenta.entries:
                str_date = time.strftime('%d/%m/%Y %H:%M:%S',entry.updated_parsed);
                print str_date  
                print entry.title
                print custom_strip_tags(entry.description)
                print entry.link
        except:
            pass
