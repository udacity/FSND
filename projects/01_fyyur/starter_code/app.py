#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Shows(db.Model):
  __tablename__ = 'Shows'
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  show_time = db.Column(db.String)
  artist = db.relationship("Artist")


class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  artists = db.relationship('Shows')


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
  seeking_venue = db.Column(db.Boolean)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data = []
  venues = Venue.query.all()
  for venue in venues:
    artists = db.session.query(Artist).join(Shows).join(Venue).filter(Venue.id==venue.id).all()
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": [{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(artists),
      } for artist in artists]})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venues = Venue.query.all()
  found = [venue for venue in venues if request.form.get('search_term').lower() in venue.name.lower()]
  response = {
    "count": len(found),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0
    } for venue in found]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = []
  venue = Venue.query.filter_by(id=venue_id).first()
  shows = venue.artists
  past_shows = [
      past_show for past_show in shows if dateutil.parser.parse(past_show.show_time) < datetime.now()
    ]
  upcoming_shows =[
      up_show for up_show in shows if dateutil.parser.parse(up_show.show_time) > datetime.now()
  ]
  data.append(
    {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": "https://www.parksquarelivemusicandcoffee.com",
      "facebook_link": venue.facebook_link,
      "seeking_talent": False,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  )
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    venue = Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      phone=request.form.get('phone'),
      genres=request.form.get('genres'),
      facebook_link=request.form.get('facebook_link')
    )
    db.session.add(venue)
    db.session.commit()
  except:
    flash('An error occurred')
  finally:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  v = Venue.query.get(venue_id)
  db.session.delete(v)
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artists = Artist.query.all()
  found = [artist for artist in artists if request.form.get('search_term').lower() in artist.name.lower()]
  response={
    "count": len(found),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0,
    } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  show_artist = Shows.query.join(Artist).join(Venue).filter(Artist.id == artist_id).all()
  data = []
  past_shows = [
    {"venue_id": Venue.query.filter(Venue.id == past_show.venue_id).first().id,
     "venue_name": Venue.query.filter(Venue.id == past_show.venue_id).first().name,
     "venue_image_link": Venue.query.filter(Venue.id == past_show.venue_id).first().image_link,
     "start_time": past_show.show_time
     } for past_show in show_artist if dateutil.parser.parse(past_show.show_time) < datetime.now()
  ]
  upcoming_shows = [
      up_show for up_show in show_artist if dateutil.parser.parse(up_show.show_time) > datetime.now()
  ]
  for show in show_artist:
    data.append(
      {
        "id": show.artist_id,
        "name": show.artist.name,
        "genres": show.artist.genres,
        "city": show.artist.city,
        "state": show.artist.state,
        "phone": show.artist.phone,
        "seeking_venue": False,
        "image_link": show.artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }
    )
  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  a = Artist.query.get(artist_id).first()
  artist={
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": a.facebook_link,
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": a.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.get('genres')
  artist.facebook_link = request.form.get('facebook_link')
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  v = Venue.query.get(venue_id)
  venue={
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": v.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": v.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  v = Venue.query.get(venue_id)
  v.name = request.form.get('name')
  v.city = request.form.get('city')
  v.state = request.form.get('state')
  v.phone = request.form.get('phone')
  v.genres = request.form.get('genres')
  v.facebook_link = request.form.get('facebook_link')
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.get('genres'),
      facebook_link=request.form.get('facebook_link')
    )
    print(artist.name)
    db.session.add(artist)
    db.session.commit()
  except:
    flash('An error occurred')
  finally:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = db.session.query(Shows).join(Artist).all()
  data = []
  for show in shows:
    venue = db.session.query(Venue).filter_by(id=show.venue_id).first()
    artist = db.session.query(Artist).filter_by(id=show.artist_id).first()
    data.append(
      {
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.show_time
      }
    )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    shows = Shows(
      venue_id=request.form.get('venue_id'),
      artist_id=request.form.get('artist_id'),
      show_time=request.form.get('start_time')
    )
    db.session.add(shows)
    db.session.commit()
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


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
