import datetime

from app import db

news2toponyms =  db.Table("news2toponyms", 
    db.Column ("news_id",  db.Integer, db.ForeignKey('news.id'), nullable = False),
    db.Column ("toponym_id", db.Integer, db.ForeignKey("toponyms.id"), nullable = False )
                          )

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.String, primary_key = True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    link = db.Column(db.String)
    txt = db.Column(db.String)
    toponyms_added = db.Column(db.Boolean, default = False)
    localization_added = db.Column(db.Boolean, default = False)

    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    tag = db.relationship('Tag', backref = db.backref('news', lazy = "dynamic"))

    toponyms = db.relationship("Toponyms",  
                                secondary = news2toponyms, 
                                backref = db.backref("news", lazy = "dynamic"),
                                lazy = "dynamic")



    def __init__(self, title, description, link, tag, hash, date= None):
        self.title = title
        self.description = description
        self.link = link
        self.tag = tag
        self.txt = title.lower() + description.lower()
        self.id  = hash
        if date:
            self.date = date
        else:
            self.date = datetime.datetime.utcnow()

    def __repr__(self):
        return "<News> " + self.title


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Tag> " + self.name


class Toponyms(db.Model):
    __tablename__ = "toponyms"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    loc_id = db.Column(db.Integer, db.ForeignKey('locs.id'))
    loc = db.relationship('Localization', backref = db.backref('toponyms', lazy = "dynamic"))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Toponym> " + self.name


class Localization(db.Model):
    __tablename__ = "locs"
    id = db.Column(db.Integer, primary_key = True)
    box = db.Column(db.String, unique = True) # '{"northeast": [55.8066899802915, 37.6366020802915], "southwest": [55.8039920197085, 37.6339041197085]}'
    geojson = db.Column(db.Text)
    
    def __init__(self, box, geojson):
        self.box = box
        self.geojson = geojson


