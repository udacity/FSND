# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder
from flask_wtf.csrf import CSRFProtect
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

seeder = FlaskSeeder()
seeder.init_app(app, db)

csrf = CSRFProtect(app)
current_datetime_format = '%Y-%m-%d %H:%M:%S'


def build_future_show_filter(show_list):
    def filter_future_show():
        return filter(lambda current_show: current_show['is_future'], show_list)

    return filter_future_show


def build_past_show_filter(show_list):
    def filter_past_show():
        return filter(lambda current_show: not current_show['is_future'], show_list)

    return filter_past_show


def convert_genre_string_to_list(genre_string):
    genre_search = re.search('{(.*)}', ''.join(genre_string), re.IGNORECASE)
    return genre_search.group(1).split(',')


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class RepositoryMixin:
    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            print(sys.exc_info())
            return False
        finally:
            db.session.close()

    @classmethod
    def get_list_for_select(cls):
        records = cls.query.order_by(cls.name.asc()).all()
        return [(a.id, a.name) for a in records]


class ShowListMixin:
    @classmethod
    def get_upcoming_shows(cls, show_list):
        filter_function = build_future_show_filter(show_list)
        return list(filter_function())

    @classmethod
    def get_past_shows(cls, show_list):
        filter_function = build_past_show_filter(show_list)
        return list(filter_function())


class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Venue(db.Model, ShowListMixin, RepositoryMixin):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String, unique=False, nullable=True)
    seeking_talent = db.Column(db.Boolean, unique=False, nullable=True)
    seeking_description = db.Column(db.String, unique=False, nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=True)
    shows = db.relationship('Show', backref='Venue', lazy='joined')

    def details(self):
        show_list = []

        for current_show in self.shows:
            show_list.append(current_show.details())

        upcoming_shows = Venue.get_upcoming_shows(show_list)
        past_shows = Venue.get_past_shows(show_list)

        return {
            'id': self.id,
            'name': self.name,
            'genres': convert_genre_string_to_list(self.genres),
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'num_shows': len(upcoming_shows),
            'upcoming_shows': upcoming_shows,
            'past_shows': past_shows,
            'upcoming_shows_count': len(upcoming_shows),
            'past_shows_count': len(past_shows),
            'has_shows': len(upcoming_shows) > 0 or len(past_shows) > 0
        }

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_venue_from_db(cls, venue_id):
        try:
            cls.query.filter_by(id=venue_id).delete()
            db.session.commit()
            return True
        except:
            print(sys.exc_info())
            db.session.rollback()
            return False
        finally:
            db.session.close()

    def set_attributes(self, form_values):
        setattr(self, 'seeking_talent', False)
        for keys, values in form_values:
            if keys != 'seeking_talent' and keys != 'genres':
                setattr(self, keys, values)
            if keys == 'seeking_talent':
                setattr(self, keys, True)
            if keys == 'genres':
                setattr(self, keys, request.form.getlist('genres'))

    def short(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def long(self):
        print(self)
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
        }


class Artist(db.Model, ShowListMixin, RepositoryMixin):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String, unique=False, nullable=True)
    seeking_venue = db.Column(db.Boolean, unique=False, nullable=True)
    seeking_description = db.Column(db.String, unique=False, nullable=True)
    genres = db.Column(db.ARRAY(db.String))
    shows = db.relationship('Show', backref='Artist', lazy='joined')

    def set_attributes(self, form_values):
        setattr(self, 'seeking_venue', False)
        for keys, values in form_values:
            if keys != 'seeking_venue' and keys != 'genres':
                setattr(self, keys, values)
            if keys == 'seeking_venue':
                setattr(self, keys, True)
            if keys == 'genres':
                setattr(self, keys, request.form.getlist('genres'))

    def details(self):
        show_details = []

        for current_show in self.shows:
            show_details.append(current_show.details())

        upcoming_shows = Artist.get_upcoming_shows(show_details)
        past_shows = Artist.get_past_shows(show_details)

        return {
            'id': self.id,
            'name': self.name,
            'genres': convert_genre_string_to_list(self.genres),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'upcoming_shows': upcoming_shows,
            'upcoming_shows_count': len(upcoming_shows),
            'past_shows': past_shows,
            'past_shows_count': len(past_shows),
        }

    def short(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Show(db.Model, RepositoryMixin):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    artist = db.relationship('Artist', lazy='joined')
    venue = db.relationship('Venue', lazy='joined')
    displayed_start_time = ''

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def set_displayed_start_time(self, timezone='America/Chicago'):
        self.displayed_start_time = convert_to_local(self.start_time.strftime(current_datetime_format), timezone) \
            .strftime(current_datetime_format)

    def is_future(self):
        current_utc = datetime.utcnow()
        pst = pytz.timezone('UTC')
        utc_time = pst.localize(self.start_time)
        current_utc = pst.localize(current_utc)
        if (utc_time - current_utc).total_seconds() > 0:
            return True
        else:
            return False

    def details(self, timezone_string='America/Chicago'):
        self.set_displayed_start_time(timezone_string)
        return {
            'venue_id': self.venue.id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'artist_id': self.artist.id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': self.displayed_start_time,
            'is_future': self.is_future()
        }

    def artist_details(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

    def venue_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = Venue.query.order_by(Venue.state.asc(), Venue.city.asc(), Venue.name.asc()).all()
    result = []
    added_locations = []

    for venue in data:
        current_location_text = ','.join([venue.city, venue.state])
        current_location_index = 0
        try:
            current_location_index = added_locations.index(current_location_text)
        except ValueError:
            added_locations.append(current_location_text)
            result.append({'city': venue.city, 'state': venue.state, 'venues': [], 'count': 0})
            current_location_index = added_locations.index(current_location_text)
        finally:
            result[current_location_index]['venues'].append(venue.details())
            result[current_location_index]['count'] = len(result[current_location_index]['venues'])

    return render_template('pages/venues.html', areas=result)


@app.route('/venues/search', methods=['POST'])
@csrf.exempt
def search_venues():
    # Search for venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    venue_list = list(map(Venue.short, venue_query))
    response = {
        "count": len(venue_list),
        "data": venue_list
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_query = Venue.query.get(venue_id)

    if venue_query:
        venue_details = Venue.details(venue_query)
        return render_template('pages/show_venue.html', venue=venue_details)
    return render_template('errors/404.html')


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm()
    if venue_form.validate_on_submit():
        new_venue = Venue()
        new_venue.set_attributes(request.form.items())
        if new_venue.save_to_db():
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!', 'success')
        else:
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.', 'failed')
        return render_template('pages/home.html')
    else:
        flash('Invalid venue form data', 'error')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('forms/new_venue.html', form=venue_form, errors=venue_form.errors)


@app.route('/venues/<venue_id>', methods=['DELETE'])
@csrf.exempt
def delete_venue(venue_id):
    result = Venue.delete_venue_from_db(venue_id)
    return jsonify({'success': result})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.order_by(Artist.name.asc()).all()
    result = []
    for artist in data:
        result.append(artist.details())
    return render_template('pages/artists.html', artists=result, artist_count=len(result))


@app.route('/artists/search', methods=['POST'])
@csrf.exempt
def search_artists():
    # Search for artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artist_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
    artist_list = list(map(Artist.short, artist_query))
    response = {
        "count": len(artist_list),
        "data": artist_list
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist_query = Artist.query.get(artist_id)
    if artist_query:
        artist_details = Artist.details(artist_query)
        return render_template('pages/show_artist.html', artist=artist_details)
    return render_template('errors/404.html')


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    current_artist = Artist.query.get(artist_id)
    form = ArtistForm(data=current_artist.details())
    return render_template('forms/edit_artist.html', form=form, artist=current_artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist_form = ArtistForm()
    current_artist = Artist.query.get(artist_id)
    if artist_form.validate_on_submit():
        current_artist.set_attributes(request.form.items())
        if current_artist.save_to_db():
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully updated!', 'success')
        else:
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.', 'failed')
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash('Invalid artist form data', 'error')
        return render_template('forms/edit_artist.html', form=artist_form, artist=current_artist,
                               errors=artist_form.errors)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    current_venue = Venue.query.get(venue_id)
    form = VenueForm(data=current_venue.details())
    return render_template('forms/edit_venue.html', form=form, venue=current_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_form = VenueForm()
    current_venue = Venue.query.get(venue_id)
    # Take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    if venue_form.validate_on_submit():
        current_venue.set_attributes(request.form.items())
        if current_venue.save_to_db():
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully updated!', 'success')
        else:
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.', 'failed')
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash('Invalid show form data', 'error')
        return render_template('forms/edit_venue.html', form=venue_form, venue=current_venue, errors=venue_form.errors)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    artist_form = ArtistForm()

    if artist_form.validate_on_submit():
        new_artist = Artist()
        new_artist.set_attributes(request.form.items())
        # insert form data in the db
        if new_artist.save_to_db():
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            # on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.', 'failed')
        return render_template('pages/home.html')
    else:
        flash('Invalid artist form data', 'error')
        return render_template('forms/new_artist.html', form=artist_form, errors=artist_form.errors)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    show_list = db.session.query(Show).order_by(Show.start_time.desc()).all()
    local_timezone = request.args.get('timezone')
    result = []
    for show in show_list:
        result.append(show.details(local_timezone))
    return render_template('pages/shows.html', shows=result, show_count=len(result))


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    form.set_artist_choice(Artist.get_list_for_select())
    form.set_venue_choice(Venue.get_list_for_select())
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_form = ShowForm()
    show_form.set_artist_choice(Artist.get_list_for_select())
    show_form.set_venue_choice(Venue.get_list_for_select())
    # called to create new shows in the db, upon submitting new show listing form
    if show_form.validate_on_submit():
        new_show = Show(
            request.form.get('venue_id'),
            request.form.get('artist_id'),
            convert_to_utc(request.form.get('start_time'))
        )
        if new_show.save_to_db():
            # on successful db insert, flash success
            flash('Show was successfully listed!', 'success')
        else:
            # e.g., flash('An error occurred. Show could not be listed.')
            flash('Show could not be listed! Please try again later.', 'failed')
        return render_template('pages/home.html')
    else:
        flash('Invalid show form data', 'error')
        return render_template('forms/new_show.html', form=show_form, errors=show_form.errors)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


@app.after_request
def apply_caching(response):
    response.headers["X-TimeZone"] = "America/Chicago"
    return response


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
