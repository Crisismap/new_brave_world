#-*- coding: UTF-8 -*-
import numpy as np
import data

import csv
import random
from gensim.models import word2vec
import os
import theano
import theano.tensor as T
import time
import sys
from sklearn.metrics import f1_score
import annots
import lasagne
import classifier

CORPUS = 'training_sets/CF-eng-hyphen-plus'  # english trainig corpus hyphens +
winsize = 2
modelfile = 'word2vec/wiki-100.model' # no commas
word2vec_model = word2vec.Word2Vec.load_word2vec_format(modelfile, binary=False)

#os.remove('/home/anna/Documents/News Classifier/CF-eng-no-commas/.~lock.1999.csv#')
path = os.path.abspath(__file__)
cwd = os.path.dirname(path)
def main(shape, model='mlp', num_epochs=100):

    files = os.listdir(CORPUS)
    random.shuffle(files)

    X_train, words_train, y_train = data.mklsts(CORPUS, files, winsize, word2vec_model, lang = 'eng')

    # we build the net
    input_var = T.dtensor3('inputs')
    target_var = T.ivector('targets')
    engine = classifier.Engine(input_var, data.build_mlp, shape, target_var = target_var)

    engine.fit(X_train, y_train, num_epochs)
    np.savez(os.path.join(cwd,'models/model-eng.npz') , *lasagne.layers.get_all_param_values(engine.network))

    print 'model saved'

if __name__ == '__main__':
    main(((None,3,word2vec_model.vector_size + 1), 150), num_epochs = 100)

