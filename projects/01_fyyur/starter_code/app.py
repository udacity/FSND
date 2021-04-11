#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
import datetime
from flask import (
  Flask, render_template, request, 
  Response, flash, redirect, url_for, abort, jsonify
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import app, db, Venue, Show, Artist

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

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

def get_shows_by_date(shows):
  try:
    # get current time to use for show time comparisons
    timeNow = datetime.now()
    showsByDate = {'pastShows':[], 'upcomingShows':[]}
    for show in shows:
      print(show.showdate)
      venue = Venue.query.get(show.venue_id)
      if show.showdate >= timeNow:
        showsByDate['upcomingShows'].append({
          'artist_id': show.artists[0].id,
          'venue_id': venue.id,
          'venue_name': venue.name,
          'artist_name': show.artists[0].name,
          'artist_image_link': show.artists[0].image_link,
          'venue_image_link': venue.image_link,
          'start_time': show.showdate.strftime('%Y-%m-%d %H:%S:%M')
        })
      else:
        showsByDate['pastShows'].append({
          'artist_id': show.artists[0].id,
          'venue_id': venue.id,
          'venue_name': venue.name,
          'artist_name': show.artists[0].name,
          'artist_image_link': show.artists[0].image_link,
          'venue_image_link': venue.image_link,
          'start_time': show.showdate.strftime('%Y-%m-%d %H:%S:%M')
        })
  except:
    print(sys.exc_info())
  return showsByDate


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
  venuesErrors = False
  try:
    # select venues, order/filter by city
    venuesByArea = []
    existingAreas = []
    venues = Venue.query.all()
    
    for venue in venues:
      areaFound = False
      venueData = {
        "id": venue.id,
        "name": venue.name,
      }

      # Check existing areas
      areaKey = venue.city.lower() + "-" + venue.state.lower()
      if areaKey in existingAreas:
        areaFound = True

      if areaFound:
        # just add venue to existing area
        areaIndex = venuesByArea.index(areaKey) 
        areaVenue = venuesByArea[areaIndex]
        areaVenue["venues"].append(venueData)
      else:
        # Make new area entry for venues in this area
        existingAreas.append(areaKey)
        areaVenue = {
          "city": venue.city, 
          "state": venue.state,
          "venues": [venueData]
        }
        # Append venue data to area venue
        venuesByArea.append(areaVenue)
  except:
    venuesErrors = True
    
  return render_template('pages/venues.html', areas=venuesByArea)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venueSearchTerm = request.form['search_term'].lower()
  searchTerm = "%{}%".format(venueSearchTerm)
  print(searchTerm)
  error = False
  venueSearchResults = []
  try:
    venues = Venue.query.filter(Venue.name.ilike(searchTerm)).all()
    for venue in venues:
      print(venue.id)
      venueData = {
        'id': venue.id,
        'name': venue.name
      }
      venueSearchResults.append(venueData)
  except:
    error = True

  response={
    "count": len(venues),
    "data": venueSearchResults
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venueError = False
  venueData = {}
  try: 
    venue = Venue.query.get(venue_id)
    genre_list = venue.genres.split(",")
    showData = get_shows_by_date(venue.shows)
    venueData = {
      "id": venue.id,
      "name": venue.name,
      "genres": genre_list,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": showData['pastShows'],
      "upcoming_shows": showData['upcomingShows'],
      "past_shows_count": len(showData['pastShows']),
      "upcoming_shows_count": len(showData['upcomingShows']),
    }
  except:
    venueError = True
  return render_template('pages/show_venue.html', venue=venueData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  createError = False
  try:
    venueName = request.form['name']
    venueCity = request.form['city']
    venueState = request.form['state']
    venueAddr = request.form['address']
    venuePhone = request.form['phone']
    venueImg = request.form['image_link']
    venueWebsite = request.form['website']
    venueGenres = ','.join(request.form.getlist('genres'))
    venueFb = request.form['facebook_link']
    venueTalentDescr = request.form['seeking_description']
    seekingTalent = False

    if 'seeking_talent' in request.form:
      print("Seeking")
      venueTalent = request.form['seeking_talent']
      if venueTalent.lower() == 'y':
        seekingTalent = True
    newVenue = Venue(
      name=venueName, 
      city=venueCity,
      state=venueState,
      address=venueAddr,
      phone=venuePhone,
      image_link=venueImg,
      facebook_link=venueFb,
      website=venueWebsite,
      genres=venueGenres,
      seeking_talent=seekingTalent,
      seeking_description='')

    if seekingTalent:
      newVenue.seeking_description = venueTalentDescr

    db.session.add(newVenue)
    db.session.commit()
  except:
    createError = True
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  if createError:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  showsToDelete = False
  deleteError = False
  try:
    # Get shows with this venu
    shows = Show.query.filter_by(venue_id=venue_id).all()
    for show in shows:
      showsToDelete = True
      db.session.delete(show)
    
    # Commit the show deletions
    if showsToDelete:
      db.session.commit()

    print("Deleted Show okay")
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    print("Deleted Venue okay")
    
  except:
    db.session.rollback()
    deleteError = True
  finally:
    db.session.close()

  if deleteError:
    print(sys.exc_info())
    abort(500)
  else:
    return jsonify({"success": True})

  # return render_template('home.html')
  # return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepagex

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artistData = []
  error = False
  try:
    artists = Artist.query.order_by('id').all()

    for artist in artists:
      artistObj = {
        'id': artist.id,
        'name': artist.name
      }
      print(artistObj)
      artistData.append(artistObj)

  except:
    error = True

  return render_template('pages/artists.html', artists=artistData)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artistSearchTerm = request.form['search_term'].lower()
  searchTerm = "%{}%".format(artistSearchTerm)
  print(searchTerm)
  error = False
  artistSearchResults = []
  try:
    artists = Artist.query.filter(Artist.name.ilike(searchTerm)).all()
    for artist in artists:
      artistData = {
        'id': artist.id,
        'name': artist.name,
      }
      
      artistSearchResults.append(artistData)
  except:
    error = True

  response={
    "count": len(artists),
    "data": artistSearchResults
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artistData = {}
  try:
    artist = Artist.query.get(artist_id)
    artistShows = artist.shows
    showData = get_shows_by_date(artistShows)

    genre_list = artist.genres.split(",")
    artistData = {
      "id": artist.id,
      "name": artist.name,
      "genres": genre_list,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "image_link": artist.image_link,
      "past_shows": showData['pastShows'],
      "upcoming_shows": showData['upcomingShows'],
      "past_shows_count": len(showData['pastShows']),
      "upcoming_shows_count": len(showData['upcomingShows'])
    }
  except:
    error = True
    print(sys.exc_info())

  return render_template('pages/show_artist.html', artist=artistData)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  try:
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    artist.genres = artist.genres.split(",")
    
  except:
    editError = True
    print("Error")
    print(sys.exc_info())

  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  editError = False
  try:
    artistName = request.form['name']
    artistCity = request.form['city']
    artistState = request.form['state']
    artistPhone = request.form['phone']
    artistImg = request.form['image_link']
    artistWebsite = request.form['website']
    artistGenres = ','.join(request.form.getlist('genres'))
    artistFb = request.form['facebook_link']
    artistSeeking = False

    if 'seeking_venue' in request.form:
      seekingFormval = request.form['seeking_venue']
      if seekingFormval.lower() == 'y':
        artistSeeking = True
          
    artist = Artist.query.get(artist_id)
    artist.name=artistName,
    artist.city=artistCity
    artist.state=artistState
    artist.phone=artistPhone
    artist.genres=artistGenres
    artist.image_link=artistImg
    artist.facebook_link=artistFb
    artist.website=artistWebsite
    artist.seeking_venue=artistSeeking

    db.session.commit()
  except:
    editError = True
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  try:
    venueObj = Venue.query.filter_by(id=venue_id).first_or_404()
    venueObj.genres = venueObj.genres.split(",")
  except:
    editError = True
    print("Error")
    print(sys.exc_info())

  form = VenueForm(obj=venueObj)
  return render_template('forms/edit_venue.html', form=form, venue=venueObj)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  editError = False
  try:
    venueName = request.form['name']
    venueCity = request.form['city']
    venueState = request.form['state']
    venueAddr = request.form['address']
    venuePhone = request.form['phone']
    venueImg = request.form['image_link']
    venueWebsite = request.form['website']
    venueGenres = ','.join(request.form.getlist('genres'))
    venueFb = request.form['facebook_link']
    venueTalentDescr = request.form['seeking_description']
    seekingTalent = False

    if 'seeking_talent' in request.form:
      venueTalent = request.form['seeking_talent']
      if venueTalent.lower() == 'y':
        print("seeking")
        seekingTalent = True
    
    venueObj = Venue.query.get(venue_id)
    venueObj.name = venueName
    venueObj.city=venueCity
    venueObj.state=venueState
    venueObj.address=venueAddr
    venueObj.phone=venuePhone
    venueObj.image_link=venueImg
    venueObj.facebook_link=venueFb
    venueObj.website=venueWebsite
    venueObj.genres=venueGenres
    venueObj.seeking_talent=seekingTalent
    venueObj.seeking_description = venueTalentDescr

    db.session.commit()
  except:
    editError = True
    print(sys.exc_info())
    db.session.rollback()

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
  createError = False
  try:
    artistName = request.form['name']
    artistCity = request.form['city']
    artistState = request.form['state']
    artistPhone = request.form['phone']
    artistImg = request.form['image_link']
    artistWebsite = request.form['website']
    artistGenres = ','.join(request.form.getlist('genres'))
    artistFb = request.form['facebook_link']
    artistSeeking = False

    if 'seeking_venue' in request.form:
      seekingFormval = request.form['seeking_venue']
      if seekingFormval.lower() == 'y':
        artistSeeking = True
          
    newArtist = Artist(
      name=artistName, 
      city=artistCity,
      state=artistState,
      phone=artistPhone,
      genres=artistGenres,
      image_link=artistImg,
      facebook_link=artistFb,
      website=artistWebsite,
      seeking_venue=artistSeeking)

    db.session.add(newArtist)
    db.session.commit()
  except:
    createError = True
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  if createError:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at   
  data = []
  try:
    shows = Show.query.order_by('id').all()
    for show in shows:
      artist = show.artists[0]
      venue = Venue.query.get(show.venue_id)
      showData = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        # "start_time": format_datetime(str(show.showdate))
        "start_time": str(show.showdate)
      }
      data.append(showData)

  except:
    error = True
    print(sys.exc_info())

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  createError = False
  errorDescr = ''
  try:
    venueId = request.form['venue_id']
    artistId = request.form['artist_id']
    startTime = request.form['start_time']
    artist = Artist.query.get(artistId)
    venue = Venue.query.get(venueId)
    if artist == None:
      errorDescr += 'Artist not found. '
      createError = True
    if venue == None:
      errorDescr += 'Venue not found. '
      createError = True
    if not createError:
      newShow = Show(
        venue_id=int(venueId),
        showdate=startTime)
      newShow.artists = [artist]

      db.session.add(newShow)
      db.session.commit()
  except:
    createError = True
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  if createError:
    flash('Show could not be listed: ' + errorDescr)
  else:
    flash('Show was successfully listed!')
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
