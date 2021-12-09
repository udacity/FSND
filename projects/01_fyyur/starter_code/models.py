from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Base = declarative_base()

class Venue(Base):
    __tablename__ = 'Venue'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    city = Column(String(120), nullable = False)
    state = Column(String(120), nullable = False)
    address = Column(String(120), nullable = False)
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    genres = Column(String(120), nullable = False)
    seeking_talent= Column(Boolean)
    seeking_description= Column(String(500))
    website = Column(String(120))
    #Relation Many Shows to One venue. Venue is the Parent
    venues = relationship("Show", backref="venue")
    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>' 

    # [X] TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(Base):
    __tablename__ = 'Artist'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    city = Column(String(120), nullable = False)
    state = Column(String(120), nullable = False)
    phone = Column(String(120))
    genres = Column(String(120), nullable = False)
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    website = Column(String(120))
    seeking_venue = Column(Boolean)
    seeking_description = Column(String(120))
    #Relation Many Shows to One venue. Venue is the Parent
    artists = relationship("Show", backref="artist")
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>' 
    
    # [ x] TODO: implement any missing fields, as a database migration using Flask-Migrate

# [ x] TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(Base):
  __tablename__ = 'Show'
  
  id = Column(Integer, primary_key=True)
  start_time = Column(DateTime)
  #Relation Many Shows to One venue. Show is the Child
  venue_id = Column(Integer,ForeignKey('Venue.id'), nullable=False)
  #Relation Many Shows to One Artist. Show is the Child
  artist_id = Column(Integer,ForeignKey('Artist.id'), nullable=False)