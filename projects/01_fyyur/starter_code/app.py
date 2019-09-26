#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

migrate = Migrate(app=app, db=db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


shows = db.Table('shows',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)


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
    all_shows = db.relationship('Artist', secondary=shows, backref=db.backref(
      'venues'
    ))




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

  data = Venue.query.all()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term').lower()

  venues = Venue.query.all()
  data = [venue for venue in venues if search_term in venue.name.lower()]
  data = [{
    "id": venue.id,
    "name": venue.name,
    "num_upcoming_shows": len(venue.shows)
  } for venue in data]
  count = len(data)
  results = {
      "count": count,
      "data": data
    }

  return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).all()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')

  venue = Venue(name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                genres=genres,
                facebook_link=facebook_link)

  try:
    db.session.add(venue)
    db.session.commit()
  except:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id)
  db.session.delet(venue)
  db.commit()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = [{
    "id": artist.id,
    "name": artist.name
  } for artist in artists ]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    artists = Artist.query.all()
    data = [{
          "id": a.id,
          "name": a.name,
          "num_upcoming_shows": len(a.venues)
      } for a in artists if search_term in a.name.lower()]
    response = {
          "count": len(data),
          "data": data
      }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artists = Artist.query.all()
  data = [
    {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "upcoming_shows": artist.venues,
    "past_shows_count": len(artist.venues),
  } for artist in artists]

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # artist.name = request.form.get
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name'),
  artist.city = request.form.get('city'),
  artist.state = request.form.get('state'),
  artist.phone = request.form.get('phone'),
  artist.genres = request.form.get('genres'),
  artist.facebook_link = request.form.get('facebook_link')
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.genres = request.form.get('genres')
  venue.facebook_link = request.form.get('facebook_link')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  create artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['get'])
def create_artist_form():
  form = artistform()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['post'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try:
    artist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.get('genres'),
      facebook_link=request.form.get('facebook_link')
    )
    db.session.add(artist)
    db.session.commit()
  except:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  all_venues = Venue.query.all()
  data = []
  for venue in all_venues:
      for artist in venue.all_shows:
          data.append({
              "venue_id": venue.id,
              "venue_name": venue.name,
              "artist_id": artist.id,
              "artist_name": artist.name,
              "artist_image": artist.image_link,
              "start_time": "2019-05-21T21:30:00.000Z"
          })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
      artist = Artist.query.filter_by(id=request.form.get('artist_id')).first()
      venue = Venue.query.filter_by(id=request.form.get('venue_id')).first()
      venue.all_shows.append(artist)
      db.session.commit()
  except:
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
      # on successful db insert, flash success
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
