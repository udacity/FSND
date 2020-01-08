#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'
    __table_args__ = (db.UniqueConstraint('name', 'city'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='')
    facebook_link = db.Column(db.String(120), nullable=False, default='')
    genres = db.Column(db.ARRAY(db.Text), nullable=False)
    website = db.Column(db.String(120), nullable=False, default='')
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=False, default='')
    shows=db.relationship('Show', backref='show_venue', cascade='all, delete, delete-orphan')

class Artist(db.Model):
    __tablename__ = 'Artist'
    __table_args__ = (db.UniqueConstraint('name', 'city'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.Text), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='')
    facebook_link = db.Column(db.String(120), nullable=False, default='')
    website = db.Column(db.String(120), nullable=False, default='')
    seeking_venues = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=False, default='')
    shows=db.relationship('Show', backref='show_artist', cascade='all, delete, delete-orphan')

class Show(db.Model):
    __tablename__ = 'Show'
    __table_args__ = (db.UniqueConstraint('artist_id', 'start_time'), )

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

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
  data=[]

  for venueLocation in Venue.query.order_by(Venue.city, Venue.state).distinct(Venue.city):
    venues = []
    for venue in Venue.query.filter_by(city=venueLocation.city):
      venueInfo = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
      }
      venues.append(venueInfo)
    
    location = {
      "city": venueLocation.city,
      "state": venueLocation.state,
      "venues": venues
    }
    data.append(location)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchTerm=request.form.get('search_term', '')
  venueData=[]
  
  venues = Venue.query.filter(Venue.name.ilike(f'%{searchTerm}%'))
  for venue in venues:
    venueInfo={
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
    }
    venueData.append(venueInfo)

  searchResult={
    "count": venues.count(),
    "data": venueData
  }

  return render_template('pages/search_venues.html', results=searchResult, search_term=searchTerm)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue=Venue.query.filter_by(id=venue_id).first_or_404()
  pastShows=[]
  upcomingShows=[]

  for show in venue.shows:
    if show.start_time > datetime.now():
      upcomingshow={
        "artist_id": show.artist_id,
        "artist_name": show.show_artist.name,
        "artist_image_link": show.show_artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
      }
      upcomingShows.append(upcomingshow)
    else:
      pastshow={
        "artist_id": show.artist_id,
        "artist_name": show.show_artist.name,
        "artist_image_link": show.show_artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
      }
      pastShows.append(pastshow)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows)
  }

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
    venue=VenueForm()

    venue_name=venue.data['name']
    venue_city=venue.data['city']
    venue_state=venue.data['state']
    venue_address=venue.data['address']
    venue_phone=venue.data['phone']
    venue_genres=venue.data['genres']
    venue_image=venue.data['image_link']
    venue_website=venue.data['website']
    venue_facebook=venue.data['facebook_link']
    venue_seeking_talent=venue.data['seeking_talent']
    venue_seeking_description=venue.data['seeking_description']

    venue=Venue(name=venue_name,city=venue_city,state=venue_state,address=venue_address,phone=venue_phone,genres=venue_genres,image_link=venue_image, website=venue_website,facebook_link=venue_facebook,seeking_talent=venue_seeking_talent,seeking_description=venue_seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except IntegrityError:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' already exists for ' + request.form['city'] + '.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be added.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[]

  for artist in Artist.query.order_by(Artist.name).all():
    artistInfo={
      "id": artist.id,
      "name": artist.name
    }
    data.append(artistInfo)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  searchTerm=request.form.get('search_term', '')
  artistData=[]

  artists = Artist.query.filter(Artist.name.ilike(f'%{searchTerm}%'))
  for artist in artists:
    artistInfo={
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.now()).count()
    }
    artistData.append(artistInfo)

  searchResult={
    "count": artists.count(),
    "data": artistData
  }

  return render_template('pages/search_artists.html', results=searchResult, search_term=searchTerm)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist=Artist.query.filter_by(id=artist_id).first_or_404()
  pastShows=[]
  upcomingShows=[]
  
  for show in artist.shows:
    if show.start_time > datetime.now():
      upcomingshow={
        "venue_id": show.venue_id,
        "venue_name": show.show_venue.name,
        "venue_image_link": show.show_venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
      }
      upcomingShows.append(upcomingshow)
    else:
      pastshow={
        "venue_id": show.venue_id,
        "venue_name": show.show_venue.name,
        "venue_image_link": show.show_venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
      }
      pastShows.append(pastshow)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.filter_by(id=artist_id).first_or_404()

  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "image_link": artist.image_link.replace('None',''),
    "website": artist.website.replace('None',''),
    "facebook_link": artist.facebook_link.replace('None',''),
    "seeking_venues": artist.seeking_venues,
    "seeking_description": artist.seeking_description.replace('None','')
  }

  form = ArtistForm(data=artist_data)
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist=ArtistForm()
    update_artist=Artist.query.filter_by(id=artist_id).first_or_404()

    update_artist.name=artist.data['name']
    update_artist.city=artist.data['city']
    update_artist.state=artist.data['state']
    update_artist.phone=artist.data['phone']
    update_artist.genres=artist.data['genres']
    update_artist.image_link=artist.data['image_link']
    update_artist.website=artist.data['website']
    update_artist.facebook_link=artist.data['facebook_link']
    update_artist.seeking_venues=artist.data['seeking_venues']
    update_artist.seeking_description=artist.data['seeking_description']

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.filter_by(id=venue_id).first_or_404()

  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "image_link": venue.image_link.replace('None',''),
    "website": venue.website.replace('None',''),
    "facebook_link": venue.facebook_link.replace('None',''),
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description.replace('None','')
  }

  form=VenueForm(data=venue_data)
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue=VenueForm()
    update_venue=Venue.query.filter_by(id=venue_id).first_or_404()

    update_venue.name=venue.data['name']
    update_venue.city=venue.data['city']
    update_venue.state=venue.data['state']
    update_venue.address=venue.data['address']
    update_venue.phone=venue.data['phone']
    update_venue.genres=venue.data['genres']
    update_venue.image_link=venue.data['image_link']
    update_venue.website=venue.data['website']
    update_venue.facebook_link=venue.data['facebook_link']
    update_venue.seeking_talent=venue.data['seeking_talent']
    update_venue.seeking_description=venue.data['seeking_description']

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  
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
    newArtist=ArtistForm()

    artist_name=newArtist.data['name']
    artist_city=newArtist.data['city']
    artist_state=newArtist.data['state']
    artist_phone=newArtist.data['phone']
    artist_genres=newArtist.data['genres']
    artist_image=newArtist.data['image_link']
    artist_website=newArtist.data['website']
    artist_facebook=newArtist.data['facebook_link']
    artist_seeking_venues=newArtist.data['seeking_venues']
    artist_seeking_description=newArtist.data['seeking_description']

    artist=Artist(name=artist_name,city=artist_city,state=artist_state,phone=artist_phone,genres=artist_genres,image_link=artist_image,website=artist_website,facebook_link=artist_facebook,seeking_venues=artist_seeking_venues,seeking_description=artist_seeking_description)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except IntegrityError:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' already exists for ' + request.form['city'] + '.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be added.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Artist was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be deleted.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  data=[]
  
  for show in Show.query.order_by(Show.start_time).all():
    showInfo={
    "venue_id": show.venue_id,
    "venue_name": show.show_venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.show_artist.name,
    "artist_image_link": show.show_artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
    }
    data.append(showInfo)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show_artistID=request.form['artist_id']
    show_venueID=request.form['venue_id']
    show_startTime=request.form['start_time']

    show=Show(artist_id=show_artistID,venue_id=show_venueID,start_time=show_startTime)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except IntegrityError:
    db.session.rollback()
    flash('An error occurred. Show on ' + show_startTime + ' already exists for Artist ID ' + show_artistID + '.')
  except:
    db.session.rollback()
    flash('An error occurred. Show on ' + show_startTime + ' could not be added.')
  finally:
    db.session.close()

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
