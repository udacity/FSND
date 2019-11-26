from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import db

engine = create_engine('postgresql:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Venue(Base):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    def __init__(self, name,  city, state, image_link, address=None, phone=None, genres=[], facebook_link=None):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = facebook_link
        # TODO: implement any missing fields

class Artist(Base):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    def __init__(self, name,  city, state, image_link, phone=None, genres=[], facebook_link=None):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.genres = genres
        self.facebook_link = facebook_link
        # TODO: implement any missing fields

# TODO Implement Show and Artist models, and complete all model relationships and properties


# Method that Creates the tables.
Base.metadata.create_all(bind=engine)
