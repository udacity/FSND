#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
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
migrate = Migrate(app, db)
# TODO-check: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'show_table'

  show_id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime(), nullable=False)

  artist = db.relationship('Artist', back_populates='shows')
  venue = db.relationship('Venue', back_populates='shows')

  def toDict(self):
    """ Returns a dict representation of instance attributes """
    showDict = {
      "show_id": self.show_id,
      "artist_id": self.artist_id,
      "venue_id": self.venue_id,
      "start_time": self.start_time
    }
    return showDict

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    
    shows = db.relationship('Show', back_populates='venue')

    def __repr__(self):
      return f'<{self.name} in {self.city}, {self.state}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', back_populates='artist')

    def __repr__(self):
      return f'<Artist: {self.name} in {self.city}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  """ Renders venues overview page """  
  data = []
  try:
    cities = db.session.query(Venue.city, Venue.state).group_by(Venue.city).group_by(Venue.state).all()
    newcity = {}

    for city in cities:
      newcity['city'] = city[0]
      newcity['state'] = city[1]
      newcity['venues'] = []
      venues = Venue.query.filter_by(city=newcity['city']).all()
      for venue in venues:
        newcity['venues'].append({
          'id' : venue.id,
          'name' : venue.name,
          "num_upcoming_shows": len([show for show in venue.shows if show.start_time < datetime.now()]),
        })
      data.append(newcity)
      newcity = {}
  except:
    flash('Could not fetch Venues data!')
    raise Exception(f'Venues: {venue.name}')
  finally:
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()

  data = []
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()]),
    })

  response={
    "count": len(venues),
    "data": data,
  }
  return render_template('pages/search_venues.html', results=response, search_term=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """ Renders the detailed page of a given Venue specified by venue_id """
  # Select Venue based on venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  
  # Select and sort shows in the Venue
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    show_data = {
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%d/%m/%y')
    }
    if show.start_time < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  data={
    "id":       venue.id,
    "name":     venue.name,
    "genres":   ('' if venue.genres is None else venue.genres.split(';')),
    "address":  venue.address,
    "city":     venue.city,
    "state":    venue.state,
    "phone":    venue.phone,
    "website":  venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  """ Renders venue insertion form in new_venue.html """
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """ Insert new_venue.html form data into the database
  
  Input:
  -- request.form: transmitted through POST methods, fields according to Venue DB Model
  """
  data = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    facebook_link = request.form['facebook_link'],
    image_link = request.form['image_link'],
    genres = ';'.join(request.form.getlist('genres')),
    seeking_talent = request.form['seeking_talent'],
    seeking_description = request.form['seeking_description']
  )

  try:
    db.session.add(data)
    db.session.commit()
    data = db.session.query(Venue).order_by(Venue.id.desc()).first()
    flash('Venue ' + data.name + ' was successfully listed!')

  except:
    db.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')

  finally:
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  """ Deletes selected venue by venue_id """
  flash_message = ''
  try:
    name = Venue.query.filter_by(id=venue_id).first().name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash_message = f'You deleted the { name } venue.'
  except:
    db.session.rollback()
    flash_message = f'Could not delete { name } venue.'
  finally:
    # known bug; flashing doesn't show after javascript redirect
    flash(flash_message)

    # returns a redirect to venues; javascript would reload the same page after delition
    return redirect(url_for('venues'), code=303)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  """ Renders the Artist overview page """
  data = []
  try:
    artists = db.session.query(Artist).order_by(Artist.name).all()
    for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name,
      })
  except:
    flash('Could not fetch Artist data!')
    raise Exception(f'Venues: {artist.name}')
  finally:
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()

  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()]),
    })

  response={
    "count": len(artists),
    "data": data,
  }
  return render_template('pages/search_artists.html', results=response, search_term=search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """ Renders the detailed page of a specific artist with artist_id """

  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.filter_by(id = artist_id).first()

  past_shows = []
  upcoming_shows = []

  for show in artist.shows:
    show_data = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%d/%m/%y')
    }
    if show.start_time < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": ('' if artist.genres is None else artist.genres.split(';')),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
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
  data = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(state=data.state, genres=data.genres.split(';'), seeking_venue=int(data.seeking_venue))
  artist={
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(';'),
    "city": data.city,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "image_link": data.image_link,
    "seeking_description": data.seeking_description,
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.image_link = request.form['image_link']
  artist.website = request.form['website']
  artist.genres = ';'.join(request.form.getlist('genres'))
  artist.seeking_venue = bool(int(request.form['seeking_venue']))
  artist.seeking_description = request.form['seeking_description']
  
  try:
    db.session.commit()
    flash(f'You succesfully updated the {artist.name} venue.')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash(f'Your modifications to {artist.name} venue were not saved!')
  finally:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  """ Renders the edit_venue.html page, populates the FORM with existing data from the db 
  specified by venue_id """
  data = Venue.query.filter_by(id=venue_id).first()
  
  # Good practice to set Selectfield elements before Form rendering rather than in Jinja 
  form = VenueForm(state=data.state, genres=data.genres.split(';'), seeking_talent=int(data.seeking_talent))

  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(';'),
    "address": data.address,
    "city": data.city,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  """ Receives venue data from edit_venue.html, updates selected venue by venue_id with data """

  if Venue.query.filter_by(id=venue_id).first():
    venue = Venue.query.filter_by(id=venue_id).first()
    
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.genres = ';'.join(request.form.getlist('genres'))
    venue.seeking_talent = bool(int(request.form['seeking_talent']))
    venue.seeking_description = request.form['seeking_description']
    
    try:
      db.session.commit()
      flash(f'You succesfully updated the {venue.name} venue.')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash(f'Your modifications to {venue.name} venue were not saved!')
    finally:
      return redirect(url_for('show_venue', venue_id=venue_id))
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """ Insert new_artist.html form data into the database
  
  Input:
  -- request.form: transmitted through POST methods, fields according to Venue DB Model
  """
  data = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    facebook_link = request.form['facebook_link'],
    website = request.form['website'],
    genres = ';'.join(request.form.getlist('genres')),
    seeking_venue = bool(int(request.form['seeking_venue'])),
    seeking_description = request.form['seeking_description']
  )

  try:
    db.session.add(data)
    db.session.commit()
    data = db.session.query(Venue).order_by(Venue.id.desc()).first()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except Exception as e:
    print(e)
    db.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  finally:
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  """ displays list of shows at /shows """

  data = []
  for show in Show.query.all():
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """ Creates a show by linking Artist - Venue in an Association Object """

  venue = Venue.query.filter_by(id=request.form['venue_id']).first()
  show = Show(
    venue_id = request.form['venue_id'],
    artist_id = request.form['artist_id'],
    start_time = request.form['start_time']
  )

  try:
    venue.shows.append(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    if app.debug:
      print(e)

    db.rollback()
    flash('Could not list show!')
  finally:
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
