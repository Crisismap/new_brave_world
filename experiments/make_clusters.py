#-*- coding: UTF-8 -*-

import pdb
import os
from math import cos, sin, radians
from argparse import ArgumentParser
import datetime as dt
import numpy as np
import pandas as pd
from pandas import DataFrame
import scipy.cluster.hierarchy as hcluster
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def handle_args():
    parser = ArgumentParser()
    parser.add_argument("-f", "--fname", default = 'Crisismap - all news.csv')
    args = parser.parse_args()
    return args

def cartesian(lat, long):
    return (cos(radians(lat)) * cos(radians(long)), cos(radians(lat)) * sin(radians(long)), sin(radians(lat)))

cartesian_vectorize = np.vectorize(cartesian)

def main():
    args = handle_args()
    fname = args.fname
    df = pd.read_csv(fname, sep = ';', encoding = "utf8")
    df = df.ix[np.random.permutation(df.index)]
    df = df[:1000]
    #df["text"] = df.Title.map(unicode) + df.Description.map(unicode)

    cartesian_coordinates = [(x,y,z) for x,y,z in zip(*cartesian_vectorize(df.lat, df.long))]
    for dim, ind in zip(("x", "y", "z"), (0, 1, 2)):
        df[dim] = [elem[ind] for elem in cartesian_coordinates]
    thresh = 0.2
    model= DBSCAN(eps = 0.1)
    cols = ["0", "1", "2", "x", "y", "z"]
    scaler = StandardScaler()
    data = scaler.fit_transform(df.fillna(0)[cols])
    #df["clusters"] =  model.fit_predict(data)
    df["clusters"] = hcluster.fclusterdata(data, thresh, metric="euclidean", criterion='distance', method = 'weighted')
    df.sort_values("clusters", inplace = True)

    now = dt.datetime.now().isoformat().replace(":", "_")
    result_name = "_".join([os.path.splitext(fname)[0], now , "result.csv"])
    #columns = ["clusters", "lat", "long"]
    #"phrases", "lat", "long", "pub_date", "type", "Title", "Description", "text"]
    columns = ["clusters", "lat", "long", "Title", "Description"]
    df[columns].to_csv(result_name, encoding = "utf8", sep = "\t", index = False)

if __name__ == "__main__":
    main()
