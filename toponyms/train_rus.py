#-*- coding: UTF-8 -*-
import numpy as np
import random, csv
from gensim.models import word2vec
import os, data
import theano
import theano.tensor as T
import time
import annots
import lasagne
import pymorphy2
import classifier
morph = pymorphy2.MorphAnalyzer()
np.set_printoptions(threshold='nan')
import gensim


CORPUS = 'training_sets/CF-rus-hyphen-plus'
winsize = 1
modelfile = 'word2vec/100-sg-hs-joint.model'
word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(modelfile, binary=False)

path = os.path.abspath(__file__)
cwd = os.path.dirname(path)

def main(shape, num_epochs=100):
    print 'main'
    print len(os.listdir(CORPUS))
    files = os.listdir(CORPUS) #[:150]
    random.shuffle(files)
    print 'getting data'
    #train data + evaluation data
    X_train, y_train = data.mklsts(CORPUS, files, winsize)#, word2vec_model, lang = 'rus')
    #X_val,  words_val, y_val = data.mklsts(CORPUS, fs2, winsize, word2vec_model, lang = 'eng')

    # we build the net
    input_var = T.dmatrix('inputs')
    target_var = T.ivector('targets')
    print 'engine'
    engine = classifier.Engine(input_var, data.build_mlp, shape, word2vec_model, 'rus', target_var = target_var)
    print 'fit'
    engine.fit(X_train, y_train, num_epochs)
    np.savez(os.path.join(cwd,'models/model-rus.npz') , *lasagne.layers.get_all_param_values(engine.network))

    print 'model saved'



if __name__ == '__main__':
    main(((None,3 * (word2vec_model.vector_size * 2 + 1)), 300), num_epochs = 100)
