import pdb
import gensim
import pandas as pd
import numpy as np

from argparse import ArgumentParser
from collections import Counter
from gensim import corpora
from itertools import chain
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import RussianStemmer
from pandas import DataFrame

#for clustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def handle_args():
    parser = ArgumentParser()
    parser.add_argument("-f", "--fname", default = 'allnews.csv')
    args = parser.parse_args()
    return args


corpus_name = "corpus.mm"
stemmer = RussianStemmer()

def is_cyrillic(symbol): return ord(symbol)>128
def cyr(some_string): return any(is_cyrillic(s) for s in some_string) and not "the" in some_string.lower()
def is_number(some_string): return all(symbol.isdigit() for symbol in some_string)

def make_df(fname = "/Users/fminlos/my_projects/Crisismap_-_all_news/Crisismap - all news.csv", n = 1000):
    df = pd.read_csv(fname, sep= ";", encoding = "utf8")
    df = df[df.type.isin(["ukraine",  "fires", "ecology", "floods"])]
    df["rus"] = df.Description.fillna("").map(cyr)
    df = df[df.rus == True]
    df = df.ix[np.random.permutation(df.index)]
    df = df[:n]
    df["text"] = df.Title + df.Description
    df["tokenized_text"] = df.text.map(lambda x: word_tokenize(x) if not pd.isnull(x) else [])
    df["tokenized_text"] = df.tokenized_text.map(lambda x: [stemmer.stem(word) for word in x])
    return df

def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))

def make_clusters(df):
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000, min_df=2)
    X = vectorizer.fit_transform(dataset.data)

def make_corpus(df, limit = 60):
    counter = Counter(chain.from_iterable(df.tokenized_text))
    counter = filter(lambda x: x[1]>3, counter.items())
    counter = filter(lambda x: len(x[0])> 2, counter)
    counter = filter(lambda x: not is_number(x[0]), counter)
    counter = sorted(counter, key = lambda x: x[1], reverse = True)
    counter = counter[limit:]
    new_dict = dict(counter)

    df["clean_text"] = df.tokenized_text.map(lambda x: filter(lambda y: y in new_dict, x))
    dictionary = corpora.Dictionary(df.clean_text)
    corpus = [dictionary.doc2bow(text) for text in df.clean_text]
    corpora.MmCorpus.serialize('corpus.mm', corpus)
    return corpus, dictionary

def get_main_topic(topics):
    try:
        return sorted(topics, key = lambda x: x[1], reverse = True)[0]
    except:
        pass


def modeling(corpus, dictionary, df, num_topics = 10):
    def most_important_words(model, n):
        for id, probability in model.show_topic(n):
              print "\t".join([str(n), dictionary[int(id)].encode('utf8'), str(probability)])
        print "\n"

    model = gensim.models.LdaModel(corpus, num_topics = num_topics)
    #model = gensim.models.LsiModel(corpus)
    for i in range(num_topics):
        most_important_words(model, i)


    results = []
    for i, doc in enumerate(corpus):
        topic, predict = get_main_topic(model[doc])
        result = dict(topic = topic, predict = predict, title =df.iloc[i].Title, description = df.iloc[i].Description)
        results.append(result)
    result  = DataFrame(results)
    for theme in result.topic.unique():
        print result[result.topic == theme].sort("predict", ascending = False).head(10)

    result[["topic", "predict", "description", "title"]].to_csv("result.csv", encoding = "utf8", sep = "\t", index = False)

args = handle_args()
fname = args.fname
df = make_df(fname, n = 300)
corpus, dictionary = make_corpus(df)
model = gensim.models.LdaModel(corpus, num_topics = 3)
df.reset_index(inplace = True)
vector_df = DataFrame([dict(elem) for elem in model[corpus]])
result = vector_df.merge(df, left_index = True, right_index = True)
result= result[[0, 1, 2, "lat", "long", "Title", "Description"]]
result.to_csv("gensim_result.txt", encoding = "utf8", sep = ";", index = False)
#modeling(corpus, dictionary, df, num_topics = 3)


