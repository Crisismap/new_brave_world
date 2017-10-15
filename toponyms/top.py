#-*- coding: UTF-8 -*-

import os
from gensim.models import word2vec
import gensim

import annots

import pymorphy2
import geocoder
from classifier import *
morph = pymorphy2.MorphAnalyzer()

path = os.path.abspath(__file__)
cwd = os.path.dirname(path)

def iseng(text):
    lat = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    cyr = u'цукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0'
    return sum(1 for l in text if l in lat ) > sum(1 for l in text if l in cyr)

g = geocoder.google('Mountain View, CA')

#word2vec models

eng_word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(os.path.join(cwd, 'word2vec/wiki-100.model'),
                                                            binary=False)
rus_word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(os.path.join(cwd,'word2vec/100-sg-hs-joint.model'),
                                                            binary=False)
# trained models
eng_model = os.path.join(cwd,'models/model-eng.npz')
rus_model = os.path.join(cwd,'models/model-rus.npz')
input_var = T.dmatrix('inputs')

#   building nets for russian and english
ru_engine = Engine(input_var, data.build_mlp, ((None,603), 300), rus_word2vec_model, 'rus', model = rus_model)
eng_engine = Engine(input_var, data.build_mlp, ((None, 303),150), eng_word2vec_model, 'eng', model = eng_model)

def extract_toponyms(text):

    words = data.get_tokens(text)
    #print ' '.join(words).encode('utf-8')
    if iseng(text):
        nn = data.neurons(words, 2, eng_word2vec_model, lang = 'eng')
        pred = eng_engine.predict(nn)
    else:
        nn = data.neurons(words, 1, rus_word2vec_model)
        pred = ru_engine.predict(nn)

    predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
    #  each one has a type (Location) and offsets (in terms of tokens)

    for top in set(annots.setlabels(words,predannotations)):
        yield top


