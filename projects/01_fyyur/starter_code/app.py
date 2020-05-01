#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, json
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy, inspect
from sqlalchemy import func, literal_column, case
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import traceback
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__, static_url_path='/static')
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

artist_show = db.Table(
  'artist_show',
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
  db.Column('show_id', db.Integer, db.ForeignKey('Show.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.PickleType)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='delete')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # !DONE 
    def __repr__(self):
      col_names = self.__table__.columns.keys()
      li = [col + ': ' + str(getattr(self,col)) for col in col_names]
      s = f" | ".join(li)
      return f'{s}'
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', secondary=artist_show, lazy=True, back_populates='artists', cascade='delete')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # !DONE
    def __repr__(self):
      col_names = self.__table__.columns.keys()
      li = [col + ': ' + str(getattr(self,col)) for col in col_names]
      s = f" | ".join(li)
      return f'{s}'
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  
  
class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    artists = db.relationship('Artist', secondary=artist_show, lazy=True, back_populates='shows', cascade='delete')

    def __repr__(self):
      col_names = self.__table__.columns.keys()
      li = [col + ': ' + str(getattr(self,col)) for col in col_names]
      s = f" | ".join(li)
      return f'{s}'
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# !DONE


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # !DONE

  case_shows_upcoming = case(
      [
        (Show.start_time > str(datetime.now()), Show.id)
      ], 
      else_=literal_column("NULL")
  )
  res = db.session.query(
    Venue.id
    , Venue.venue_name
    , func.count( case_shows_upcoming ).label('upcoming_shows')
    , Venue.city
    , Venue.state
  ).join(Show, isouter=True
  ).group_by(Venue.id
  ).all()

  venues_by_city = {}
  for row in res:
    venue_id, name, upcoming_shows, city, state = row
    venue = {
      "id": venue_id
      , "name": name
      , "num_upcoming_shows": upcoming_shows
    }
    try:
      venues_by_city[city]["venues"].add(venue)
    except:
      venues_by_city[city] = {"venues":[venue], "state":state, "city":city}

  d = [venues_by_city[city] for city in venues_by_city.keys()]
    
  return render_template('pages/venues.html', areas=d);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # !DONE
  search_for = request.form.get('search_term', '')
  result = db.session.query(Venue).filter(Venue.venue_name.ilike(f'%{search_for}%')).all()
  
  response={
    "count": len(result),
    "data": [{
      "id": row.id,
      "name": row.venue_name,
      "num_upcoming_shows": len(row.shows),
    } for row in result]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_for)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # !DONE

  shows_q = db.session.query(
    Artist.id, Artist.name, Artist.image_link, Show.start_time 
    ).join(Show, Venue.shows
    ).join(Artist, Show.artists
    ).filter(Venue.id == venue_id).all()

  upcoming_shows = [{
      "artist_id": show[0],
      "artist_name": show[1],
      "artist_image_link": show[2],
      "start_time": str(show[3])
    } for show in shows_q if show[3] > datetime.now()]
  past_shows = [{
      "artist_id": show[0],
      "artist_name": show[1],
      "artist_image_link": show[2],
      "start_time": str(show[3])
    } for show in shows_q if show[3] <= datetime.now()]

  result = db.session.query(Venue).get(venue_id).as_dict()
  result = {key:value_formatted(key,val) for key, val in result.items()}
  result.update({
    'upcoming_shows': upcoming_shows,
    'past_shows': past_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
    })
  
  return render_template('pages/show_venue.html', venue=result)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():  
  data = request.get_json()
  try:
    new_venue = get_or_create(Venue, name=data['venue_name'], data=data)
    db.session.add(new_venue)
    db.session.commit()
    resp = Venue.query.order_by(Venue.id.desc()).first()
    return json.jsonify(resp.as_dict())
  except:
    db.session.rollback()
    print('Rolled back.\nError:', traceback.format_exc())
    return 'something went wrong, debug:' + str(traceback.format_exc()), 400
  finally:
    db.session.close()
  # TODO: insert form data as a new Venue record in the db, instead
  # !DONE
  # TODO: modify data to be the data object returned from db insertion
  # !DONE

  # on successful db insert, flash success
  # ! Implemented alert in View instead
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/  
  # ! Implemented bad request response with traceback logged in view instead

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # !DONE
  try:
    venue = db.session.query(Venue).get(venue_id)
    print('deleting:', venue)
    db.session.delete(venue)
    db.session.commit()
    return json.jsonify(venue_id)
  except:
    db.session.rollback()
    print('Something went wrong:', traceback.format_exc())
    return 'Error:' + traceback.format_exc(), 200
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # !DONE

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # !DONE
  res = db.session.query(Artist).all()
  d = [{"id": row.id, "name": row.name} for row in res]
  
  return render_template('pages/artists.html', artists=d)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = db.session.query(Artist).get(artist_id)
    print('deleting:', artist)
    db.session.delete(artist)
    db.session.commit()
    return json.jsonify(artist_id)
  except:
    db.session.rollback()
    print('Something went wrong:', traceback.format_exc())
    return 'Error:' + traceback.format_exc(), 200
  finally:
    db.session.close()

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # !DONE
  search_for = request.form.get('search_term', '')
  result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_for}%')).all()

  response={
    "count": len(result),
    "data": [{
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows": len(row.shows),
    } for row in result]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_for)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # !DONE
  shows_q = db.session.query(
    Show.venue_id, Venue.venue_name, Venue.image_link, Show.start_time 
    ).join(Show, Artist.shows
    ).join(Venue
    ).filter(Artist.id == artist_id).all()

  upcoming_shows = [{
      "venue_id": show[0],
      "venue_name": show[1],
      "venue_image_link": show[2],
      "start_time": str(show[3])
    } for show in shows_q if show[3] > datetime.now()]
  past_shows = [{
      "venue_id": show[0],
      "venue_name": show[1],
      "venue_image_link": show[2],
      "start_time": str(show[3])
    } for show in shows_q if show[3] <= datetime.now()]

  result = db.session.query(Artist).get(artist_id).as_dict()
  result = {key:value_formatted(key,val) for key, val in result.items()}
  result.update({
    'upcoming_shows': upcoming_shows,
    'past_shows': past_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
    })

  return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=db.session.query(Artist).get(artist_id).as_dict()
  art_li = {key:value_formatted(key, val) for key,val in artist.items()}
  form = ArtistForm(**art_li)
  # TODO: populate form with fields from artist with ID <artist_id>
  # !DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  data = {key:val for key,val in request.form.items() if key != 'genres'}
  data.update({'genres':request.form.getlist('genres')})

  try:
    artist = db.session.query(Artist).get(artist_id)
    for key, val in data.items():
      setattr(artist, key, val)
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:
    db.session.rollback()
    print('something went wrong', traceback.format_exc())
    return 'error:' + traceback.format_exc(), 200
  finally:
    db.session.close()  

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes 
  # !DONE

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=db.session.query(Venue).get(venue_id).as_dict()
  ven_li = {key:value_formatted(key, val) for key,val in venue.items()}
  form = VenueForm(**ven_li)
  # TODO: populate form with values from venue with ID <venue_id>
  #!DONE
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  data = {key:val for key,val in request.form.items() if key != 'genres'}
  data.update({'genres':request.form.getlist('genres')})

  try:
    venue = db.session.query(Venue).get(venue_id)
    for key, val in data.items():
      setattr(venue, key, val)
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  except:
    db.session.rollback()
    print('something went wrong', traceback.format_exc())
    return 'error:' + traceback.format_exc(), 200
  finally:
    db.session.close()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  #!DONE


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  print(request.get_json())
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  #!DONE
  # TODO: modify data to be the data object returned from db insertion
  #!DONE
  data = request.get_json()
  try:
    new_artist = get_or_create(Artist, name=data['name'], data=data)
    db.session.add(new_artist)
    db.session.commit()
    resp = Artist.query.order_by(Artist.id.desc()).first()
    return json.jsonify(resp.as_dict())
  except:
    db.session.rollback()
    print('Rolled back.\nError:', traceback.format_exc())
    return 'something went wrong, debug:' + str(traceback.format_exc()), 400
  finally:
    db.session.close()
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  #!Returning bad request instead
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #!DONE

  shows = db.session.query(Venue.id, Venue.venue_name, Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Venue).join(Artist, Show.artists).all()
  d = [ {
    "venue_id": row[0],
    "venue_name": row[1],
    "artist_id": row[2],
    "artist_name": row[3],
    "artist_image_link": row[4],
    "start_time": str(row[5])
  } for row in shows]
  
  return render_template('pages/shows.html', shows=d)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  data = request.get_json() 
  try:
    show_data = {key:val for key,val in data.items() if key != 'artist_id'}
    new_show = Show(**show_data)
    show_artists = [Artist.query.filter_by(id=pk).first() for pk in data['artist_id'].split(',')]
    
    new_show.artists.append(*show_artists)

    db.session.add(new_show)
    db.session.commit()
    record = Show.query.order_by(Show.id.desc()).first()
    print('successfully inserted:', record)
    return json.jsonify(record.as_dict())
  except:
    db.session.rollback()
    print('rolled back because of error:', traceback.format_exc())
    return str(traceback.format_exc()), 200

  finally:
    db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # !DONE
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # ! Implemented with alert in view
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # !Returning bad request with traceback instead, logging in view

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


def get_or_create(Model, name, data):
  print(Model.__name__ == 'Venue')
  if Model.__name__ == 'Venue':
    exists = db.session.query(Model.id).filter_by(venue_name=name).scalar() is not None
    if exists:
        return db.session.query(Model).filter_by(venue_name=name).first()
  else:
    exists = db.session.query(Model.id).filter_by(name=name).scalar() is not None
    if exists:
        return db.session.query(Model).filter_by(name=name).first()
  return Model(**data)

def value_formatted(key, value):
    if key == 'genres' and value is not None and not isinstance(value, list):
      print(value)
      try:
        value = value.replace('{','')
        value = value.replace('}','')
      except AttributeError as err:
        value = value.replace('[','')
        value = value.replace(']','')
      finally:
        value = value.split(',')
    return value

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
