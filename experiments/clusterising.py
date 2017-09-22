#-*- coding: UTF-8 -*-

import pdb
import gensim
import pandas as pd
import numpy as np

from collections import Counter
from gensim import corpora
from itertools import chain
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import RussianStemmer
from pandas import DataFrame
import gpxpy.geo

import pygraphviz
import networkx as nx



#from sklearn.cluster import DBSCAN, AffinityPropagation, KMeans, spectral_clustering, AgglomerativeClustering
from sklearn.manifold import TSNE
tsne = TSNE(n_components=2, metric='precomputed')
#clusteriser = DBSCAN()
#clusteriser = AgglomerativeClustering(n_clusters=2, affinity='precomputed', linkage = 'average')

#clusteriser = AffinityPropagation()


#from toponyms.top import extract_toponyms
"""
for toponym in extract_toponyms(u'Ожесточенные бои идут возле Авдеевки - волонтер - РИА Новости Украина   Боевые действия  на востоке  Украины  начались в середине апреля 2014 года. В заявлении МИД, обнародованном 29 февраля, говорится, что с начала конфликта погибли более 2600  украинских  военнослужащих, свыше 9000 получили ранения. В свою очередь глава подразделения ... '):
    print toponym.encode('utf-8')

print geocoder.google('юге').latlng
print '==============================================
for toponym in extract_toponyms(u'Генштаб Украины заявил о проведении военных учений на юге страны - Rambler News Service  Украина проводит учения вооруженных сил на юге страны, сообщает Reuters со ссылкой на представителя  украинского  Генштаба. По его словам, учения начались в .... Если наши требования не будут выполнены, то прием  беженцев  будет приостановлен». Цитата дня: Реджеп Тайип ...  '):
    print toponym.encode('utf-8')
"""

#syria = pd.read_csv('Syria.csv', sep = '\t')
#ukrain = pd.read_csv('Ukrain.csv', sep = '\t')

#df = pd.concat((syria, ukrain), axis=0,ignore_index=False)
#df = df.ix[np.random.permutation(df.index)]

df = pd.read_csv('Crisismap - all news.csv', sep = ';')
df = df.ix[np.random.permutation(df.index)]
df = df[:1000]
#print df

results, lats, longs = [], [],[]
for i, doc in enumerate(df.iterrows()):
    try:
        result = dict(text = df.iloc[i].Title + ' ' + df.iloc[i].Description, id = i, point = (float(df.iloc[i].lat), float(df.iloc[i].long)))
        lats.append(float(df.iloc[i].lat))
        longs.append(float(df.iloc[i].long))
        results.append(result)

    except:
        print 'except'

#coords =

from math import cos, sin, radians
def cartesian(lat, long):
    return (cos(radians(lat)) * cos(radians(long)), cos(radians(lat)) * sin(radians(long)), sin(radians(lat)))

cartesian_vectorize = np.vectorize(cartesian)

cartesian_coordinates = [(x,y,z) for x,y,z in zip(*cartesian_vectorize(lats, longs))]
print cartesian_coordinates
#np.apply_along_axis(cartesian,0, (np.ndarray(lats), np.ndarray(longs)))

def distance(top0,top1):

    lon0 =  top0[1]
    lon1 =  top1[1]
    lat0 =  top0[0]
    lat1 =  top1[0]

    dist = gpxpy.geo.haversine_distance(lat0, lon0, lat1, lon1)
    return dist

points = []
distance_matrix = np.zeros((len(results), len(results)))
for i,r0 in enumerate(results):
        points.append(r0['point'])
        for j,r1 in enumerate(results):
            #try:

                distance_matrix[i,j] = distance(r0['point'], r1['point'] ) / 10000

            #except:
            #    distance_matrix[i,j] = 1000



"""
X_embedded = tsne.fit_transform(distance_matrix)
print X_embedded.shape
Y = np.max(X_embedded[:,1])
X = np.max(X_embedded[:,0])
y = np.min(X_embedded[:,1])
x = np.min(X_embedded[:,0])


data_to_cluster = np.asarray([[X_embedded[i,0], X_embedded[i,1]] for i in xrange(X_embedded.shape[0])])
"""
import scipy.cluster.hierarchy as hcluster

thresh = 0.2
#clusters = hcluster.fclusterdata(data_to_cluster, thresh, criterion="distance")
#clusters = hcluster.fclusterdata(cartesian_coordinates, thresh, metric="cosine", criterion='distance', method = 'complete')


clusters = hcluster.fclusterdata(cartesian_coordinates, thresh, metric="euclidean", criterion='distance', method = 'weighted')


import csv
rs = [_ for _ in zip(*sorted(zip(results,  clusters), key=lambda x: x[1]))]
texts_sort, y_sort = rs[0], rs[1]
with open('clusters.csv', 'w') as fout:
        writer = csv.writer(fout, delimiter = '\t')
        for text, label in zip(texts_sort, y_sort):

            writer.writerow([text['text'] , str(label) ,text['point'], str(cartesian(text['point'][0], text['point'][1]))])


#print X,Y
#print data_to_cluster
#clusters = clusteriser.fit_predict(data_to_cluster)


import matplotlib.pyplot as plt
tsne_vec = TSNE(n_components=2, metric='cosine')

X_embedded = tsne.fit_transform(distance_matrix)
print X_embedded.shape
Y = np.max(X_embedded[:,1])
X = np.max(X_embedded[:,0])
y = np.min(X_embedded[:,1])
x = np.min(X_embedded[:,0])




plt.plot(X_embedded[:,0], X_embedded[:,1], 'ro')
plt.axis([x-2, X + 2, y-2, Y + 2])
#for i,txt in enumerate(points):
for i,txt in enumerate(clusters):

#for i,txt in enumerate(zip(clusters, points)):

    plt.annotate(txt, (X_embedded[i,0], X_embedded[i,1]))
    #plt.annotate(txt, (X_embedded[-6:,0][i], X_embedded[-6:,1][i]))
plt.show()
"""

plt.plot(X_embedded[:,0], X_embedded[:,1], 'ro')
plt.axis([x-2, X + 2, y-2, Y + 2])
for i,txt in enumerate(points):
#for i,txt in enumerate(clusters):

#for i,txt in enumerate(zip(clusters, points)):

    plt.annotate(txt, (X_embedded[i,0], X_embedded[i,1]))
    #plt.annotate(txt, (X_embedded[-6:,0][i], X_embedded[-6:,1][i]))
plt.show()



import codecs
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import  TaggedDocument
import os, csv


import string
exclude = set(string.punctuation)
def del_commas(text):
    return ''.join(s for s in text if s not in exclude)

import pandas as pd
files = ('Crisismap - all news.csv', '/home/anchen/Documents/news_corpus_no_commas.txt')


class LS(object):
    def __init__(self, files):
        self.files = files
    def __iter__(self):
        for file in files:
            print file
            if file[-4:] == '.csv':
                df =pd.read_csv(file, sep= ";", encoding = "utf8")
                for i, row in enumerate(df.iterrows()):
                    #print df.iloc[i].Title, df.iloc[i].Description
                    try:
                        text = del_commas(df.iloc[i].Title + ' ' + df.iloc[i].Description)

                        yield(TaggedDocument(text.split(), ['csv_%s' % i]))
                    except:
                        print 'except'
            else:
                with open(file, 'r') as fin:
                    for j, text in enumerate(fin.readlines()):
                        yield(TaggedDocument(del_commas(text).split(), ['txt_%s' % j]))


sentences = LS(files)

model = Doc2Vec(alpha=0.025, min_alpha=0.025)  # use fixed learning rate
model.build_vocab(sentences)
for epoch in range(10):
    model.train(sentences)
    model.alpha -= 0.002  # decrease the learning rate
    model.min_alpha = model.alpha  # fix the learning rate, no decay

model.save('models/doc2vec.model')


#model = Doc2Vec(size=20, min_count=2, iter=55)
#model.build_vocab(train_data)
#model.train(train_data, total_examples=model.corpus_count, epochs=model.iter)

#model.save('doc2vec.model')

#model = Doc2Vec(documents, size=100, window=8, min_count=5, workers=4)

"""