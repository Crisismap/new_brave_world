#-*- coding: UTF-8 -*-

import os
from gensim.models import KeyedVectors

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
        for word, cls in zip(words, pred):
            if word in data.rus_gazeteers_keys:
                data.rus_gazeteers[word].add(cls)

    else:
        nn = data.neurons(words, 1, rus_word2vec_model)
        pred = ru_engine.predict(nn)
        for word, cls in zip(words, pred):
            if word in data.eng_gazeteers_keys:
                data.eng_gazeteers[word].add(cls)


#    for word, cls in zip(words, pred):
#        if word in data.rus_gazeteers_keys() and (cls == '1' or cls == '2'):
#            data.rus_gazeteers[word].add(cls)
#        elif cls == '1' or cls == '2':
#            data.rus_gazeteers_keys.add(word)
#            data.rus_gazeteers[word] = cls

    predannotations = annots.setAnnotations(pred,  {1: 'Location'})  # list of annotations
    #  each one has a type (Location) and offsets (in terms of tokens)

    for top in annots.setlabels(words,predannotations):
        yield top


