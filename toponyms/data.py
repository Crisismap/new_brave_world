#-*- coding: UTF-8 -*-
import pymorphy2
import numpy as np
import os,csv
import re
import lasagne
import cPickle as pickle
np.set_printoptions(threshold='nan')

morph = pymorphy2.MorphAnalyzer()

path = os.path.abspath(__file__)
cwd = os.path.dirname(path)

def norm_gram(token):
    parse = morph.parse(token)
    if len(parse) > 0:
        return (parse[0].normal_form, reduce(lambda x,y : x + '_' + str(y), sorted(parse[0].tag.grammemes), ''))
    else:
        return (token,'zero')



def iscap(word):
    capitalised = False
    cap = lambda _ : len(_) > 0 and _[0].isupper() and (len(_) == 1 or _[1:].islower())
    if cap(word):
        capitalised = True
    else:
        parts = word.split('-')
        if cap(parts[0]) and all(cap(_) or _.islower() for _ in parts):
            capitalised = True
    return capitalised

def rus_vector(word, model):
    (normal, grammar) = norm_gram(word)
    if normal  in model.vocab and grammar in model.vocab:

        return list(model[normal]) + list(model[grammar]) + [iscap(word),]# word1, word2]
    elif grammar in model.vocab:
        return list(model['unk']) + list(model[grammar]) +  [iscap(word),]# word1, word2]
    else:
        return list(model['unk']) + [0] * model.vector_size + [iscap(word),]# word1, word2]

def eng_vector(word, model):
    if word.lower()  in model.vocab:
        return list(model[word.lower()]) + [iscap(word),]# word1, word2]
    else:
        return list(model['unk']) + [iscap(word),]# word1, word2]

def mean(listoflists):
    return listoflists[0]


def neurons(words, winsize, model, lang = 'rus'):
    words = [u'<fullstop>'] * winsize + words[:-1] + [u'<fullstop>'] * winsize
    ns = []
    if lang == 'rus':
        for j, word in enumerate(words[winsize:-winsize]):
            i = j + winsize

            ns.append(mean([rus_vector(_, model) for _ in words[i - winsize: i]]) + rus_vector(word, model)
                      + mean([rus_vector(_, model) for _ in  words[i + 1: i + winsize + 1]]))
    else:
        for j, word in enumerate(words[winsize:-winsize]):
            i = j + winsize
            ns.append(mean([eng_vector(_, model) for _ in words[i - winsize: i]]) + eng_vector(word, model)
                      + mean([eng_vector(_, model) for _ in  words[i + 1: i + winsize + 1]]))
    return ns

def mklsts (CORPUS, files, winsize):
    WORDS, CLS = [], []
    for file in files:
        #print file
        with open (os.path.join(CORPUS, file), 'r') as f:
            words,cls = [], []
            reader = csv.reader(f, delimiter = '\t')
            for row in reader:
                words.append(row[0].decode('utf-8'))
                cls.append(int(row[1]))
        cls.extend([0] *  (winsize - 1))
        WORDS.extend(words)
        WORDS.extend(['<fullstop>'] * (winsize - 1))
        CLS.extend(cls)

    print len(WORDS), np.asarray(CLS, dtype = 'int32').shape
    return WORDS, np.asarray(CLS, dtype = 'int32')


def  get_tokens(text): #split to tokens
    text = re.sub(ur'&quot;', ur'"', text)
    text = re.sub(ur'([ ^$][йцукенгшщзхъфывапролджэячсмитьбю0-9a-z]+)([\-])', ur'\1 \2 ', text)
    text = re.sub(ur'([\-])([йцукенгшщзхъфывапролджэячсмитьбю0-9a-z]+)', ur' \1 \2', text)
    #split to sentences
    text = re.sub(ur'[ <>\[\]]', ' ', text)#
    text = re.sub(ur',[ ]*([.!?]+)', ur'<fullstop>', text)
    text = re.sub(ur'([^ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z])([.!?]+)[ \n]+([ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z])',ur'\1 <fullstop> \3', text)
    text = re.sub(ur'([^ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z])([.!?]+)[ ]*$',ur'\1 <fullstop> ', text)
    text = re.sub(ur'([ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z]+[ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z]+)([.!?]+)', ur'\1 <fullstop>', text)
    text = re.sub(ur'([\.,:;!\?\=/&\(\)»„“"”«—%])', ur' \1 ', text)
    text = re.sub(ur'([йцукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0-9a-zA-Z\+])(["»„\)])', ur'\1 \2', text)
    text = re.sub(ur'([\(“"«])([йцукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0-9a-z-A-Z\+])', ur'\1 \2', text)
    text = re.sub(ur'[ ]+', ' ', text)
    words = text.split()
    return words

def del_commas(source):
    text = re.sub(ur'&quot;', ur'"', source)
    text = re.sub(ur'([\.,:;!\?\=\-—/&"»„\)\(“«])', ur' ', text)
    text = re.sub(ur'[ ]+', ' ', text)
    return text

def Pr (result, response):
    try:
        return  len(result.intersection(response))/float(len(result))
    except:
        print 'no true results'
        return 0

def Re (result, response):
    try:
        return len(response.intersection(result))/float(len(response))
    except:
        print 'no true responses'
        return 0

def f1(result, response):
    try:
        return 2 * Pr(result, response) * Re(result, response) / float(Pr (result, response) + Re(result, response) )
    except:
        print 'invalid f1'
        return 0

def scores(result, response):
    precision = Pr (result, response)
    recall = Re (result, response)
    f1 = 2 * precision * recall/float(precision + recall)
    return precision, recall, f1


def build_mlp(shape, input_var=None):

    network = lasagne.layers.InputLayer(shape=shape[0],
                                     input_var=input_var)
    #l_in_drop = lasagne.layers.DropoutLayer(l_in, p=0.2)
    for hid in shape[1:]:
        network = lasagne.layers.DenseLayer(
            network, num_units=hid,
            nonlinearity=lasagne.nonlinearities.sigmoid,
            W=lasagne.init.GlorotUniform())
    #l_hid1_drop = lasagne.layers.DropoutLayer(l_hid1, p=0.5)
    network = lasagne.layers.DenseLayer(
        network, num_units=3,
        nonlinearity=lasagne.nonlinearities.softmax)
    return network

def gen_data(words, indices, winsize, model, lang = 'rus'):
    #print 'gen_data'

    words = [u'<fullstop>'] * winsize + words
    ns = []
    if lang == 'rus':
        for j in indices:
            i = j + winsize

            ns.append(mean([rus_vector(_, model) for _ in words[i - winsize: i]]) + rus_vector(words[i], model)
                      + mean([rus_vector(_, model) for _ in  words[i + 1: i + winsize + 1]]))
    else:
        for j in indices:
            i = j + winsize

            ns.append(mean([eng_vector(_, model) for _ in words[i - winsize: i]]) + eng_vector(words[i], model)
                      + mean([eng_vector(_, model) for _ in  words[i + 1: i + winsize + 1]]))
    #print 'return ns'
    return ns


def iterate_minibatches(inputs, targets, batchsize, model, lang = 'rus', winsize = 1, shuffle=False):
    assert len(inputs) == len(targets)
    if shuffle:
        indices = np.arange(len(inputs) - winsize)
        np.random.shuffle(indices)
    for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
        if shuffle:
            excerpt = indices[start_idx:start_idx + batchsize]
        else:
            excerpt = slice(start_idx, start_idx + batchsize)

        yield gen_data(inputs,excerpt,  winsize, model, lang = lang), targets[excerpt]