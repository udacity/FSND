#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from forms import Form
import datetime
from datetime import datetime
from sqlalchemy.orm import  joinedload
from flask_migrate import Migrate
from models import Venue , Artist , Show , db

today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

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
    venues = Venue.query.all()
    data = []
    cities_states = set()
    for venue in venues:
        cities_states.add( (venue.city, venue.state) )

    cities_states = list(cities_states)
    for city in cities_states:
        venues_list = []
        for venue in venues:
            if (venue.city == city[0]) and (venue.state == city[1]):
                venue_shows = Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming = 0
                for show in venue_shows:
                    if show.start_time > today:
                        num_upcoming += 1

                venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming
                })

        data.append({
            "city": city[0],
            "state": city[1],
            "venues": venues_list
        })
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '').strip()
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    venue_list = []
    for venue in venues:
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming = 0
        for show in venue_shows:
            if show.start_time > today:
                num_upcoming += 1
        venue_list.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming
        })

    response = {
        "count": len(venues),
        "data": venue_list
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        artist = Artist.query.get(show.artist_id)
        temp_show = {
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time
        }
        if show.start_time <= today:
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    data = vars(venue)

    data["id"] = venue.id
    data["name"] = venue.name
    data["genres"] = venue.genres.split(',')
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["website"] = venue.website_link
    data["facebook_link"] = venue.facebook_link
    data["seeking_talent"] = True if venue.seeking_talent else False
    data["seeking_description"] = venue.seeking_description
    data["image_link"] = venue.image_link
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = ','.join(request.form.getlist('genres'))
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    website_link = request.form.get('website_link')

    try:
      venue = Venue(
        name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,
        facebook_link=facebook_link,genres=genres,seeking_talent=seeking_talent,
        seeking_description=seeking_description,website_link=website_link)  
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except():
      db.session.rollback()
      flash('An error occurred. Venue ' + name + ' could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
    finally:
        db.session.close()

    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist).all()
  data = []

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').strip()
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  artist_list = []
  for artist in artists:
      artist_shows = Show.query.filter_by(artist_id=artist.id).all()
      num_upcoming = 0
      for show in artist_shows:
          if show.start_time > today:
              num_upcoming += 1
      artist_list.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming
      })

  response = {
      "count": len(artists),
      "data": artist_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)

  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    venue = Venue.query.get(show.venue_id)
    temp_show = {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time
    }
    if show.start_time <= today:
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)



  data = vars(artist)

  data["id"] = artist.id
  data["name"] = artist.name
  data["genres"] = artist.genres.split(',')
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website"] = artist.website_link
  data["facebook_link"] = artist.facebook_link
  data["seeking_venue"] = True if artist.seeking_venue else False
  data["seeking_description"] = artist.seeking_description
  data["image_link"] = artist.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

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
  form.genres.data=artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form.get('image_link')
  artist.facebook_link = request.form.get('facebook_link')
  artist.website_link = request.form.get('website_link')
  artist.seeking_venue = True if request.form.get('seeking_venue') else False
  artist.seeking_description = request.form.get('seeking_description')

  db.session.commit()

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
  form.genres.data= venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.genres = request.form.getlist('genres')
  venue.image_link = request.form.get('image_link')
  venue.facebook_link = request.form.get('facebook_link')
  venue.website_link = request.form.get('website_link')
  venue.seeking_talent = True if request.form.get('seeking_talent') else False
  venue.seeking_description = request.form.get('seeking_description')

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
  form = ArtistForm(request.form)
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = ','.join(request.form.getlist('genres'))
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website_link')
  seeking_venue = True if request.form.get('seeking_venue') else False
  seeking_description = request.form.get('seeking_description')
  
  try:
    artist=Artist( name=name, city=city, state=state, phone=phone, genres=genres,
      image_link=image_link, facebook_link=facebook_link, website_link=website_link,
      seeking_venue=seeking_venue, seeking_description=seeking_description )
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
    flash('An error occurred. Artist ' + name + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = db.session.query(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Show, Show.venue_id==Venue.id).filter(Show.artist_id==Artist.id).all()

  for show in shows:
    data.append({
    "venue_id": show[0],
    "venue_name": show[1],
    "artist_id": show[2],
    "artist_name": show[3],
    "artist_image_link": show[4],
    "start_time": show[5],
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  try:
    show = Show(artist_id=artist_id,venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except ():
    flash('An error occurred. Show could not be listed.')

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