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
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import logging
import json
from datetime import datetime
from collections import defaultdict


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
class Shows(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)       
    start_time = db.Column(db.DateTime, nullable = False)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(500))
    
    shows = db.relationship('Shows', backref=db.backref('Venue', lazy=True))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(500))
     
    shows = db.relationship('Shows', backref=db.backref('Artist', lazy=True))

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
  raw_data = Venue.query.order_by(Venue.state, Venue.city).all()
  tmp_data = defaultdict(list)
  data = []
  tmp_city = ''
  tmp_state = ''
  for entry in raw_data:
        if tmp_city == '':
              tmp_data = {'city':entry.city,
                          'state':entry.state,
                          'venues':[{'id':entry.id,'name':entry.name}]
                          }
              data.append(tmp_data)
        elif tmp_city == entry.city:
              tmp_data['venues'].append({'id':entry.id,'name':entry.name})
        else:
              tmp_data = {'city':entry.city,
                         'state':entry.state,
                         'venues':[{'id':entry.id,'name':entry.name}]
                         }
              data.append(tmp_data)

        tmp_city = entry.city            
  # print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  venue_data = []
  for item in result:
        venue_data.append({
          "id": item.id,
          "name": item.name
        })
  response={
    "count": len(result),
    "data": venue_data
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  upcoming_shows_filter = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time>datetime.now()).all()
  past_shows_filter = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time<datetime.now()).all()
  
  upcoming = []
  for show in upcoming_shows_filter:
        upcoming.append({
          "artist_id": show.artist_id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')
        })
        
  past = []
  for show in past_shows_filter:
        past.append({
          "artist_id": show.artist_id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')
        })
        
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "image_link": venue.image_link,
    "facebook_link": venue.facebook_link,
    "seeking_description": venue.seeking_description,
    "seeking_talent": venue.seeking_talent,
    "website": venue.website,
    "upcoming_shows": upcoming,
    "upcoming_shows_count": len(upcoming),
    "past_shows": past,
    "past_shows_count": len(past) 
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
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')
  else:
    flash(f'Venue {venue_id} was successfully deleted.')

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  artist_data = []
  for item in result:
        artist_data.append({
          "id": item.id,
          "name": item.name
        })
  response={
    "count": len(result),
    "data": artist_data
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_item = Artist.query.get(artist_id)
  upcoming_shows_filter = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time>datetime.now()).all()
  past_shows_filter = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time<datetime.now()).all()
  
  upcoming = []
  for show in upcoming_shows_filter:
        upcoming.append({
          "venue_id": show.venue_id,
          "venue_name": show.Venue.name,
          "venue_image_link": show.Venue.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')
        })
        
  past = []
  for show in past_shows_filter:
        past.append({
          "venue_id": show.artist_id,
          "venue_name": show.Venue.name,
          "venue_image_link": show.Venue.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M')
        })
        
  data = {
    "id": artist_item.id,
    "name": artist_item.name,
    "city": artist_item.city,
    "state": artist_item.state,
    "phone": artist_item.phone,
    "genres": artist_item.genres,
    "image_link": artist_item.image_link,
    "facebook_link": artist_item.facebook_link,
    "seeking_venue": artist_item.seeking_venue,
    "seeking_description": artist_item.seeking_description,
    "website": artist_item.website,
    "upcoming_shows": upcoming,
    "upcoming_shows_count": len(upcoming),
    "past_shows": past,
    "past_shows_count": len(past) 
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(artist_id)
  
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Could not edit!')
  else: 
    flash(f'Artist {artist_id} was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Could not edit!')
  else: 
    flash(f'Venue {venue_id} was successfully updated!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows_item = db.session.query(Shows).join(Venue).join(Artist).all()

  data = []
  for show in shows_item:
    print(show)
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name, 
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
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
