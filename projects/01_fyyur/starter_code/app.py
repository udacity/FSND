#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import re
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from helpers import *
from sqlalchemy import func, case

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# [x] TODO: connect to a local postgresql database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jserra02@localhost:5432/todoapp'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app=app, db=db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable = False)
    seeking_talent= db.Column(db.Boolean)
    seeking_description= db.Column(db.String(500))
    website = db.Column(db.String(120))
    #Relation Many Shows to One venue. Venue is the Parent
    venues = db.relationship("Show", backref="venue")
    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>' 

    # [X] TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    #Relation Many Shows to One venue. Venue is the Parent
    artists = db.relationship("Show", backref="artist")
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>' 
    
    # [ x] TODO: implement any missing fields, as a database migration using Flask-Migrate

# [ x] TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime)
  #Relation Many Shows to One venue. Show is the Child
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'), nullable=False)
  #Relation Many Shows to One Artist. Show is the Child
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'), nullable=False)

def get_case_upfront():
  '''
  This case method is used several times to cound the number of show that are upfront, this way we can rehuse it
  '''
  return case(
    [
        (Show.start_time>datetime.now(), 1)  
    ],
    else_=0
  )  
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
  # [x] TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  unique_venues_location = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data=[]
  print(unique_venues_location)
  for location in unique_venues_location:
    venues = Venue.query.filter(Venue.city == location.city and Venue.state == location.state).join(Show,Show.venue_id==Venue.id, isouter=True).with_entities(Venue.id, Venue.name,Venue.city, Venue.state ,func.count(get_case_upfront()).label("num_upcoming_shows")).group_by(Venue.id, Venue.name,Venue.city, Venue.state ).order_by(Venue.id).all()
    if venues:
      list_location={}
      list_location["city"]=location.city
      list_location["state"]=location.state
      list_venues=[]
      for venue in venues:
        info={}
        info["id"] = venue.id
        info["name"] = venue.name
        info["num_upcoming_shows"] = venue.num_upcoming_shows
        list_venues.append(info)
      list_location["venues"]=list_venues
      data.append(list_location)
      
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # [ x ] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_name = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_name))).join(Show,Show.venue_id==Venue.id, isouter=True).with_entities(Venue.id, Venue.name, func.count(get_case_upfront()).label("num_upcoming_shows")).group_by(Venue.id, Venue.name).order_by(Venue.id).all()
  response = {}
  data=[]
  count_venues = 0
  for venue in venues:
    info={}
    info["id"] = venue.id
    info["name"] = venue.name
    info["num_upcoming_shows"] = venue.num_upcoming_shows
    data.append(info)
    count_venues += 1
  response["count"] = count_venues
  response["data"]=data
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # [x] TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  venue_dict={}
  venue_dict["id"]=venue.id
  venue_dict["name"]=venue.name
  venue_dict["genres"]=venue.genres.split(",")
  venue_dict["address"]=venue.address
  venue_dict["city"]=venue.city
  venue_dict["state"]=venue.city
  venue_dict["phone"]=venue.phone
  venue_dict["website"]=venue.website
  venue_dict["facebook_link"]=venue.facebook_link
  venue_dict["seeking_talent"]=venue.seeking_talent
  venue_dict["seeking_description"]=venue.seeking_description
  venue_dict["image_link"]=venue.image_link
  shows = Show.query.filter_by(venue_id=venue_id).order_by(Show.start_time).all()
  upcoming_shows=[]
  upcoming_shows_count=0
  past_shows=[]
  past_shows_count=0
  for show in shows:
    show_dict={}
    show_dict["start_time"]= castStart_time(show.start_time)
    artist = Artist.query.get(show.artist_id)
    show_dict["artist_name"] = artist.name
    show_dict["artist_image_link"] = artist.image_link
    show_dict["artist_id"] = artist.id
    if isShowUpcoming(show.start_time):
      upcoming_shows_count += 1 
      upcoming_shows.append(show_dict)
    else:
      past_shows_count += 1
      past_shows.append(show_dict)
  venue_dict["upcoming_shows"]=upcoming_shows
  venue_dict["upcoming_shows_count"]=upcoming_shows_count
  venue_dict["past_shows"]=past_shows
  venue_dict["past_shows_count"]=past_shows_count
        
      
  return render_template('pages/show_venue.html', venue=venue_dict)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # [x] TODO: insert form data as a new Venue record in the db, instead
  # [x] TODO: modify data to be the data object returned from db insertion
  try:
    input = request.form
    print("new venue")
    venue_name = input['name']
    venue_city = input['city']
    venue_state = input['state']
    venue_address = input['address']
    venue_phone = input['phone']
    venue_image_link = input['image_link']
    #In case that multiples genres are chosed, the same key appears multiple time, to concat them to string this method is needed
    print("starting new method works")
    print(input)
    venue_genres = concat_genre(input)
    print("new method works")
    venue_facebook_link = input['facebook_link']
    venue_website_link = input['website_link']
    venue_seeking_talent = get_boolean_value_dict(input,'seeking_talent')
    
    venue_seeking_description = input['seeking_description']
    venue = Venue(name=venue_name, city=venue_city, state=venue_state, address=venue_address,
                phone=venue_phone, image_link=venue_image_link, facebook_link=venue_facebook_link,
                genres=venue_genres, seeking_talent=venue_seeking_talent, seeking_description=venue_seeking_description, website=venue_website_link)
    print(venue)
    db.session.add(venue)
    #commit the session in the DB
    db.session.commit() 
    # on successful db insert, flash success
    flash('Venue ' + input['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # [x] TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue {} could not be listed.'.format(input['name']))
  finally:
    db.session.close()  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # [X] TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    for show in venue.venues:
        db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # [x] TODO: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id,Artist.name).order_by(Artist.id).all()
  data = []
  for artist in artists:
    artist_info={}
    artist_info["id"] = artist.id
    artist_info["name"] = artist.name
    data.append(artist_info)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # [x] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_name = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_name))).join(Show,Show.artist_id==Artist.id, isouter=True).with_entities(Artist.id, Artist.name, func.sum(get_case_upfront()).label("num_upcoming_shows")).group_by(Artist.id, Artist.name).order_by(Artist.id).all()
  response = {}
  data=[]
  count_shows = 0
  print(artists)
  for artist in artists:
    info={}
    info["id"] = artist.id
    info["name"] = artist.name
    info["num_upcoming_shows"] = artist.num_upcoming_shows
    data.append(info)
    count_shows += 1
  response["count"] = count_shows
  response["data"]=data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # [x] TODO: replace with real artist data from the artist table, using artist_id
  
  artists_info = Artist.query.get(artist_id)
  data = {}
  data["id"] = artists_info.id
  data["name"] = artists_info.name
  data["city"] = artists_info.city
  data["genres"] = artists_info.genres.split(',')
  data["state"] = artists_info.state
  data["website"] = artists_info.website
  data["facebook_link"] = artists_info.facebook_link
  data["seeking_venue"] = artists_info.seeking_venue
  data["seeking_description"] = artists_info.seeking_description
  data["image_link"] = artists_info.image_link
  upcoming_shows=[]
  upcoming_shows_count=0
  past_shows=[]
  past_shows_count=0
  shows = Show.query.filter_by(artist_id=artist_id).order_by(Show.start_time).all()
  for show in shows:
    show_dict={}
    show_dict["start_time"]= castStart_time(show.start_time)
    artist = Venue.query.get(show.venue_id)
    show_dict["venue_name"] = artist.name
    show_dict["venue_image_link"] = artist.image_link
    show_dict["venue_id"] = artist.id
    #To know if the show is upcoming or not, we check the date of the show vs the current date
    if isShowUpcoming(show.start_time):
      upcoming_shows_count += 1 
      upcoming_shows.append(show_dict)
    else:
      past_shows_count += 1
      past_shows.append(show_dict)
  data["upcoming_shows"]=upcoming_shows
  data["upcoming_shows_count"]=upcoming_shows_count
  data["past_shows"]=past_shows
  data["past_shows_count"]=past_shows_count
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data={}
  artist_data["id"]=artist.id
  artist_data["name"]=artist.name
  artist_data["genres"]=artist.genres.split(',')
  artist_data["city"]=artist.city
  artist_data["state"]=artist.state
  artist_data["phone"]=artist.phone
  artist_data["website"]=artist.website
  artist_data["facebook_link"]=artist.facebook_link
  artist_data["seeking_venue"]=artist.seeking_venue
  artist_data["seeking_description"]=artist.seeking_description
  artist_data["image_linkd"]=artist.image_link
  # [ x] TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # [x] TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    print(request.form)
    input = request.form
    artist = Artist.query.get(artist_id)
    artist.name=input['name']
    artist.city=input['city']
    artist.state=input['state']
    artist.phone=input['phone']
    artist.image_link=input['image_link']
    artist.facebook_link=input['facebook_link']
    artist.website=input['website_link']
    artist.seeking_description=input['seeking_description']
    #In case that multiples genres are chosed, the same key appears multiple time, to concat them to string this is needed
    artist.genres = concat_genre(input)
    artist.seeking_venue = get_boolean_value_dict(input, 'seeking_venue')
    
    db.session.commit()
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  finally:
    db.session.close()  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_data={}
  venue_data["id"]=venue.id
  venue_data["name"]=venue.name
  venue_data["genres"]=venue.genres.split(',')
  venue_data["city"]=venue.city
  venue_data["state"]=venue.state
  venue_data["address"]=venue.address
  venue_data["phone"]=venue.phone
  venue_data["website"]=venue.website
  venue_data["facebook_link"]=venue.facebook_link
  venue_data["seeking_talent"]=venue.seeking_talent
  venue_data["seeking_description"]=venue.seeking_description
  venue_data["image_linkd"]=venue.image_link

  # [x] TODO: _datapopulate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # [x] TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    input = request.form
    venue = Venue.query.get(venue_id)
    venue.name = input['name']
    venue.city = input['city']
    venue.state = input['state']
    venue.address = input['address']
    venue.phone = input['phone']
    venue.image_link = input['image_link']
    #In case that multiples genres are chosed, the same key appears multiple time, to concat them to string this is needed
    venue.genres = concat_genre(input)
    venue.facebook_link = input['facebook_link']
    venue.website_link = input['website_link']
    venue.seeking_talent = get_boolean_value_dict(input,'seeking_talent')
    venue.seeking_description = input['seeking_description']
    db.session.commit()
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
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
  # called upon submitting the new artist listing form
  # [x] TODO: insert form data as a new Venue record in the db, instead
  # [x] TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  try:
    input = request.form
    artist_name=input['name']
    artist_city=input['city']
    artist_state=input['state']
    artist_phone=input['phone']
    artist_image_link=input['image_link']
    artist_facebook_link=input['facebook_link']
    artist_website=input['website_link']
    artist_seeking_description=input['seeking_description']
     #In case that multiples genres are chosed, the same key appears multiple time, to concat them to string this is needed
    artist_genres = concat_genre(input)
    artist_seeking_venue = get_boolean_value_dict(input,'seeking_venue')
    
    artist = Artist(name=artist_name, city=artist_city, state=artist_state,
                    phone=artist_phone, genres=artist_genres, image_link=artist_image_link,
                    facebook_link=artist_facebook_link, website=artist_website, seeking_venue=artist_seeking_venue, seeking_description=artist_seeking_description)
    db.session.add(artist)
    #commit the session in the DB
    db.session.commit() 
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # [x] TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()  
    


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # [x] TODO: replace with real venues data.
  shows = Show.query.join(Artist,Artist.id == Show.artist_id).join(Venue,Venue.id == Show.venue_id ).with_entities(Show.id.label("show_id"),Show.start_time.label("start_time"),Artist.name.label("artist_name"),Artist.image_link.label("artist_image_link"), Venue.name.label("venue_name"), Show.venue_id, Show.artist_id).order_by("start_time")
  data = []
  for show in shows:
    show_info={}
    show_info["venue_id"]=show.venue_id
    show_info["venue_name"]=show.venue_name
    show_info["artist_id"]=show.artist_id
    show_info["artist_name"]=show.artist_name
    show_info["artist_image_link"]=show.artist_image_link
    show_info["start_time"]=castStart_time(show.start_time)
    data.append(show_info)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # [x] TODO: insert form data as a new Show record in the db, instead
  print(request.form)
  error = False
  try:
    show_start_time=datetime.strptime(request.form.get("start_time"),"%Y-%m-%d %H:%M:%S")
    show_artist_id=request.form.get("artist_id")
    show_venue_id=request.form.get("venue_id")
    print("creating show")
    show = Show(start_time=show_start_time, artist_id=show_artist_id, venue_id=show_venue_id)
    print("show created")
    #add the todo item into the session
    db.session.add(show)
    #commit the session in the DB
    db.session.commit() 
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print("error")
    #to see the error for debug purposes
  finally:
    db.session.close()
    #Return the JSON only if is not an error    
  if error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  
  # [x] TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
