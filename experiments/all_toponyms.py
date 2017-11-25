#-*- coding: UTF-8 -*-
import pandas as pd
from toponyms.top import extract_toponyms


#def lotop(text):
#    ts = tuple(extract_toponyms(text))
#    return ts

data = pd.read_csv('Crisismap - all news.csv', sep = ';', encoding = 'utf-8', usecols = ['Title', 'Description'])

data.dropna(inplace = True)


data['text'] = data.Title + ' ' + data.Description
data['toponyms'] = data.text.apply(lambda x: ', '.join(extract_toponyms(x)))

data.to_csv('crisismap_with_toponyms.csv', sep = '\t', encoding = 'utf-8', columns = ['Title', 'Description', 'toponyms'])