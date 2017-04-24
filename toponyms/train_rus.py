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

CORPUS = 'training_sets/CF-rus-hyphen-plus'
winsize = 2
modelfile = 'word2vec/100-sg-hs-joint.model'
word2vec_model = word2vec.Word2Vec.load_word2vec_format(modelfile, binary=False)

path = os.path.abspath(__file__)
cwd = os.path.dirname(path)

def main(shape, num_epochs=100):

    files = os.listdir(CORPUS)
    random.shuffle(files)

    #train data + evaluation data
    X_train, words_train, y_train = data.mklsts(CORPUS, files, winsize, word2vec_model, lang = 'rus')
    #X_val,  words_val, y_val = data.mklsts(CORPUS, fs2, winsize, word2vec_model, lang = 'eng')

    # we build the net
    input_var = T.dtensor3('inputs')
    target_var = T.ivector('targets')
    engine = classifier.Engine(input_var, data.build_mlp, shape, target_var = target_var)

    engine.fit(X_train, y_train, num_epochs)
    np.savez(os.path.join(cwd,'models/model-rus.npz'), *lasagne.layers.get_all_param_values(engine.network))

    print 'model saved'



if __name__ == '__main__':
    main(((None,3,word2vec_model.vector_size * 2 + 1), 300), num_epochs = 50)
