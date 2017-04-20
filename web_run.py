import os
from flask import render_template
from app import app
from db_models import *

def b(txt, word):
    for elem in  (word, word.lower(), word.capitalize(), word.upper()):
        txt = txt.replace(elem, u"<b>{elem}</b>".format(elem = elem))
    return txt

@app.route("/<word>")
def word(word):
    pattern = "%" + word.lower()  + "%"
    news = News.query.filter(News.txt.like(pattern)).all()
    titles = [b(n.title, word) for n in news]
    descriptions = [b(n.description, word) for n in news]
    ns = zip(news, titles, descriptions)
    return render_template("index.html", ns = ns)

@app.route("/map")
def map():
    return render_template("map.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

