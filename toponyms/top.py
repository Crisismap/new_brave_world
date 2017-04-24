#-*- coding: UTF-8 -*-

import os
from gensim.models import word2vec

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
eng_word2vec_model = word2vec.Word2Vec.load_word2vec_format(os.path.join(cwd, 'word2vec/wiki-100.model'),
                                                            binary=False)
rus_word2vec_model = word2vec.Word2Vec.load_word2vec_format(os.path.join(cwd,'word2vec/100-sg-hs-joint.model'),
                                                            binary=False)
# trained models
eng_model = os.path.join(cwd,'models/model-eng.npz')
rus_model = os.path.join(cwd,'models/model-rus.npz')
input_var = T.dtensor3('inputs')

# building nets for russian and english
ru_engine = Engine(input_var, data.build_mlp, ((None,3,201), 300),  model = rus_model)
eng_engine = Engine(input_var, data.build_mlp, ((None, 3, 101),150), model = eng_model)

def extract_toponyms(text):

    words = data.get_tokens(text)
    if iseng(text):
        nn = data.neurons(words, 2, eng_word2vec_model, lang = 'eng')
        pred = eng_engine.predict(nn)
    else:
        nn = data.neurons(words, 2, rus_word2vec_model)
        pred = ru_engine.predict(nn)

    predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
    #  each one has a type (Location) and offsets (in terms of tokens)

    for top in set(annots.setlabels(words,predannotations)):
        yield top


