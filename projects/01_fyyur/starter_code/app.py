#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for

from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Shows, Venue, Artist, app, db


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
  """
  Get a list of all venues
  :return: List[Dict]
  """
  data = []
  venues = Venue.query.all()
  for venue in venues:
    artists = db.session.query(Artist).join(Shows).filter(Shows.venue_id == venue.id).all()
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
  """
  Search for a specific venue
  :return: Dict
  """
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


def get_past_up_shows(shows):
  """
  A function that get a shows object and returns a tuple of lists of
  upcoming and past shows
  :param shows: Shows model
  :return: Tuple[List, List]
  """
  past_shows, upcoming_shows = [], []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    if not artist:
      return [{
        "artist_id": "NA",
        "artist_name": "NA",
        "artist_image_link": "NA",
        "start_time": "NA"
      }], [{
        "artist_id": "NA",
        "artist_name": "NA",
        "artist_image_link": "NA",
        "start_time": "NA"
      }]
    if dateutil.parser.parse(show.show_time) < datetime.now():
      past_shows.append(
        {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": show.show_time
      }
    )
    else:
      upcoming_shows.append(
        {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": show.show_time
      }
    )
  return past_shows, upcoming_shows


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """
  Show a specific venue
  :param venue_id: int
  :return: List[Dict]
  """
  shows = Shows.query.filter(Shows.venue_id == venue_id).all()
  past_shows, upcoming_shows = get_past_up_shows(shows)
  data = []
  for show in shows:
    data.append(
      {
        "id": show.venue.id,
        "name": show.venue.name,
        "genres": show.venue.genres,
        "address": show.venue.address,
        "city": show.venue.city,
        "state": show.venue.state,
        "phone": show.venue.phone,
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": show.venue.facebook_link,
        "seeking_talent": False,
        "image_link": show.venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }
    )
  return render_template('pages/show_venue.html', venue=data[0])

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  """
  A function to get the form for creating a new venue
  :return:
  """
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """
  A function to submit a new venue
  :return: None
  """
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
  """
  A function to delete a venue.
  :param venue_id: int
  :return: None
  """
  v = Venue.query.get(venue_id)
  db.session.delete(v)
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  """
  A function to list all artists
  :return: List[Dict]
  """
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
  """
  A function to search a specific artist
  :return: Dict
  """
  artists = Artist.query.all()
  found = [artist for artist in artists if request.form.get('search_term').lower() in artist.name.lower()]
  response={
    "count": len(found),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0,
    } for artist in found]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """
  A function to display a specific artist
  :param artist_id: int
  :return: Dict
  """
  artist = Artist.query.filter(Artist.id == artist_id).first()
  past_shows, upcoming_shows = get_past_up_shows(artist.venues)
  data = {
          "id": artist.id,
          "name": artist.name,
          "genres": artist.genres,
          "city": artist.city,
          "state": artist.state,
          "phone": artist.phone,
          "seeking_venue": False,
          "image_link": artist.image_link,
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcoming_shows),
        }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  """
  A function to edit an artist
  :param artist_id: int
  :return: Dict
  """
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
  """
  A function to update the artist info
  :param artist_id: int
  :return: None
  """
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
  """
  A function to display venue info to be edited
  :param venue_id: int
  :return: Dict
  """
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
  """
  A function to update venue in database
  :param venue_id: int
  :return: None
  """
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
  """
  A function to display create artist form
  :return: None
  """
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """
  A function to update artist info in DB
  :return: None
  """
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
    flash('An error occurred')
  finally:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  """
  A function to show all shows
  :return: List[Dict]
  """
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
  """
  A function to render new show form
  :return:
  """
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """
  A function to update show info in DB
  :return: None
  """
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
