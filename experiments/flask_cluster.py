import os
import pdb
from argparse import ArgumentParser
import pandas as pd
from flask import render_template

def handle_args():
    parser = ArgumentParser()
    parser.add_argument("-f", "--fname", required = True)
    parser.add_argument("-p", "--port", default = 5001)
    return parser.parse_args()

from flask import Flask, render_template

app = Flask(__name__)
app.config["SECRET_KEY"] = "Haskell"

args = handle_args()
fname = args.fname
port = args.port
df = pd.read_csv(fname, encoding = "utf8", sep = "\t")
df["cluster"] = df.clusters.map(str)

@app.route("/")
def visualize():
    return render_template("ex.html", df = df)

app.run(host='0.0.0.0', port=port)

