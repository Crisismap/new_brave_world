import os
from flask import render_template
from app import app
from db_models import *
from db_funcs import get_coords

def b(txt, word):
    for elem in  (word, word.lower(), word.capitalize(), word.upper()):
        txt = txt.replace(elem, u"<b>{elem}</b>".format(elem = elem))
    return txt

@app.route("/<word>")
def word(word):
    pattern = "%" + word.lower()  + "%"
    news = News.query.filter(News.txt.like(pattern)).all()

    ns = []
    for n in news:
        if n.loc:
           title = b(n.title, word)
           description =  b(n.title, word)
           loc = (get_coords(n.loc), n.loc.geojson)
           phrases = [toponym.name for toponym in n.toponyms if n.loc == toponym.loc]
           ns.append((n, title, description, loc, phrases))     
     #titles = [b(n.title, word) for n in news]
    #descriptions = [b(n.description, word) for n in news]
    #locs = [(get_coords(n.loc), n.loc.geojson) for  n in news] 
    #ns = zip(news, titles, descriptions, locs)
    return render_template("m.html", ns = ns)

@app.route("/map")
def map():
    return render_template("m.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)

