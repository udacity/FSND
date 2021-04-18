# ----------------------------------------------------------------------------#
# Imports
from operator import itemgetter

from flask_migrate import Migrate
import sys
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler

from sqlalchemy import func

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    looking_for_venues = db.Column(db.String, default='F')
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')


def create_search_data(id, name, num_of_shows):
    return {
        "id": id,
        "name": name,
        "num_upcoming_shows": num_of_shows
    }
# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    venues = Venue.query.order_by(Venue.city).all()

    def create_venue_data(city, state):
        return {
            "city": city,
            "state": state,
            "venues": []
        }

    current_state = None
    current_city = None
    current_venue_data = None
    data = []

    for venue in venues:

        venue_shows = Show.query.filter(Show.venue_id == venue.id)
        upcoming_shows = 0
        for show in venue_shows:
            if str_to_date(show.start_time) > datetime.now():
                upcoming_shows += 1

        def create_venue(id, name, num_upcoming_shows):
            return {
                "id": id,
                "name": name,
                "num_upcoming_shows": num_upcoming_shows
            }
        if current_city != venue.city or current_state != venue.state:
            if current_venue_data:
                data.append(current_venue_data)

            current_city = venue.city
            current_state = venue.state
            current_venue_data = create_venue_data(venue.city, venue.state)
            current_venue_data['venues'].append(create_venue(venue.id, venue.name, upcoming_shows))
        else:
            current_venue_data['venues'].append(create_venue(venue.id, venue.name, upcoming_shows))
    else:
        if current_venue_data:
            data.append(current_venue_data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(request.form['search_term']))).all()

    response = {
        "count" : len(venues),
        "data": []
    }

    for venue in venues:
        num_of_upcoming_shows = Show.query.filter(Show.venue_id == venue.id).all()
        response["data"].append(create_search_data(venue.id, venue.name, num_of_upcoming_shows))

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter(Venue.id == venue_id).first()
    venue_shows = db.session.query(Show.start_time.label('start_time'), Artist.id.label('artist_id'),
                                    Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link')).join(
        Artist).filter(Show.venue_id == venue_id).all()

    past_shows = []
    upcoming_shows = []

    for show in venue_shows:
        show_time = {
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time
        }
        if str_to_date(show['start_time']) < datetime.now():
            past_shows.append(show_time)
        else:
            upcoming_shows.append(show_time)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "looking_for_talent": venue.looking_for_talent,
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
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist(key='genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    looking_for_talent = request.form['seeking_talent']
    seeking_description = request.form['seeking_description']

    if looking_for_talent == 'F':
        looking_for_talent = False
    else:
        looking_for_talent = True

    error = False
    try:
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
                      facebook_link=facebook_link, image_link=image_link, website_link=website_link,
                      looking_for_talent=looking_for_talent, seeking_description=seeking_description, genres=genres)

        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + name + ' could not be listed.')
        else:
            flash('Venue ' + name + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = Artist.query.all()

    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    artists = Artist.query.filter(func.lower(Artist.name).contains(func.lower(request.form['search_term']))).all()

    response = {
        "count" : len(artists),
        "data": []
    }

    for artist in artists:
        num_of_upcoming_shows = Show.query.filter(Show.venue_id == artist.id).all()
        response["data"].append(create_search_data(artist.id, artist.name, num_of_upcoming_shows))

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.filter(Artist.id == artist_id).first()
    artist_shows = db.session.query(Show.start_time.label('start_time'), Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link')).join(Venue).filter(Show.artist_id == artist_id).all()

    past_shows = []
    upcoming_shows = []

    for show in artist_shows:
        show_time = {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue_name,
                    "venue_image_link": show.venue_image_link,
                    "start_time": show.start_time
        }
        if str_to_date(show['start_time']) < datetime.now():
            past_shows.append(show_time)
        else:
            upcoming_shows.append(show_time)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.looking_for_venues,
        "seeking_description": artist.seeking_description,
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
    form = ArtistForm()
    found_artist = Artist.query.filter(artist_id == Artist.id).first()
    form.name.default = found_artist.name
    form.city.default = found_artist.city
    form.phone.default = found_artist.phone
    form.state.default = found_artist.state
    form.genres.default = found_artist.genres
    form.facebook_link.default = found_artist.facebook_link
    form.image_link.default = found_artist.image_link
    form.website_link.default = found_artist.website_link
    form.seeking_venue.default = found_artist.looking_for_venues
    form.seeking_description.default = found_artist.seeking_description
    form.process()
    artist = {
        "id": found_artist.id,
        "name": found_artist.name,
        "genres": found_artist.genres,
        "city": found_artist.city,
        "state": found_artist.state,
        "phone": found_artist.phone,
        "website": found_artist.website_link,
        "facebook_link": found_artist.facebook_link,
        "seeking_venue": found_artist.looking_for_venues,
        "seeking_description": found_artist.seeking_description,
        "image_link": found_artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    artist = Artist.query.filter(Artist.id == artist_id).first()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist(key='genres')
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    artist.looking_for_venues = request.form['seeking_venue']
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist(key='genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = request.form['seeking_venue']
    seeking_description = request.form['seeking_description']

    error = False
    try:
        artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link,
                        image_link=image_link, website_link=website_link,
                        looking_for_venues=seeking_venue,
                        seeking_description=seeking_description, genres=genres)

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' + name + ' could not be listed.')
        else:
            flash('Artist ' + name + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    shows = db.session.query(Venue.id.label('venue_id'), Venue.name.label('venue_name'), Artist.id.label("artist_id"),
                            Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'),
                            Show.start_time.label('start_time')).join(Show, Artist.id == Show.artist_id)\
                            .join(Venue, Venue.id == Show.venue_id).all()


    data = []
    for show in shows:
        data.append({
        "venue_id": show["venue_id"],
        "venue_name": show["venue_name"],
        "artist_id": show["artist_id"],
        "artist_name": show["artist_name"],
        "artist_image_link": show["artist_image_link"],
        "start_time": format_datetime(show["start_time"]),
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
    # TODO: insert form data as a new Show record in the db, instead
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    error = False

    try:
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

        db.session.add(show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
