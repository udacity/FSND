#    ----------------------------------------------------------------------------#
# Imports
#    ----------------------------------------------------------------------------#

import json
import sys
import re
import dateutil.parser
import babel
import datetime
import dateparser
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler

from extensions import csrf
from forms import ShowForm, VenueForm, ArtistForm

#    ----------------------------------------------------------------------------#
# App Config.
#    ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
csrf.init_app(app)
db = SQLAlchemy(app)
# connect app and db to migration utility
migrate = Migrate(app, db)


#    ----------------------------------------------------------------------------#
# Models.
#    ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)

    @property
    def serialize_summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': self.num_upcoming_shows
        }

    @property
    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(','),
            'city': self.city.name,
            'state': self.city.state,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            'image_link': self.image_link,
            'past_shows': self.past_shows_serialized,
            'upcoming_shows': self.upcoming_shows_serialized,
            "past_shows_count": self.num_past_shows,
            "upcoming_shows_count": self.num_upcoming_shows
        }

    @property
    def past_shows(self):
        current_time = datetime.datetime.utcnow()
        return Show.query.filter(Show.venue_id == self.id, current_time > Show.start_time)\
            .order_by(Show.start_time.desc())

    @property
    def past_shows_serialized(self):
        serialized_shows = []
        for show in self.past_shows.all():
            serialized_shows.append(show.serialized_artist)
        return serialized_shows

    @property
    def num_past_shows(self):
        return self.past_shows.count()

    @property
    def upcoming_shows(self):
        current_time = datetime.datetime.utcnow()
        return Show.query.filter(Show.venue_id == self.id, current_time < Show.start_time)\
            .order_by(Show.start_time.asc())

    @property
    def upcoming_shows_serialized(self):
        serialized_shows = []
        for show in self.upcoming_shows.all():
            serialized_shows.append(show.serialized_artist)
        return serialized_shows

    @property
    def num_upcoming_shows(self):
        return self.upcoming_shows.count()


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    # past_shows
    #   venue_id, venue_name, venue_image_link, start_time
    # upcoming_shows
    #   venue_id, venue_name, venue_image_link, start_time
    # past_shows_count
    # upcoming_shows_count

    @property
    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'genres': self.genres.split(','),
            'image_link': self.image_link,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'city': self.city.name,
            'state': self.city.state,
            'past_shows': self.past_shows_serialized,
            'upcoming_shows': self.upcoming_shows_serialized,
            "past_shows_count": self.num_past_shows,
            "upcoming_shows_count": self.num_upcoming_shows
        }

    @property
    def get_past_shows(self):
        current_time = datetime.datetime.utcnow()
        return db.session.query(Show).filter(Show.start_time < current_time).filter(self.id == Show.artist_id)

    @property
    def past_shows(self):
        current_time = datetime.datetime.utcnow()
        return Show.query.filter(Show.venue_id == self.id, current_time > Show.start_time) \
            .order_by(Show.start_time.desc())

    @property
    def past_shows_serialized(self):
        serialized_shows = []
        for show in self.past_shows.all():
            serialized_shows.append(show.serialized_venue)
        return serialized_shows

    @property
    def num_past_shows(self):
        return self.past_shows.count()

    @property
    def upcoming_shows(self):
        current_time = datetime.datetime.utcnow()
        return Show.query.filter(Show.venue_id == self.id, current_time < Show.start_time) \
            .order_by(Show.start_time.asc())

    @property
    def upcoming_shows_serialized(self):
        serialized_shows = []
        for show in self.upcoming_shows.all():
            serialized_shows.append(show.serialized_venue)
        return serialized_shows

    @property
    def num_upcoming_shows(self):
        return self.upcoming_shows.count()

    @property
    def serialize_summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': self.num_upcoming_shows
        }

    @property
    def serialize_minimal(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    @property
    def serialized_artist(self):
        return {
            'artist_id': self.artist.id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': self.start_time.isoformat()
        }

    @property
    def serialized_venue(self):
        return {
            'venue_id': self.venue.id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'start_time': self.start_time.isoformat()
        }


class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    venues = db.relationship('Venue', backref='city', lazy=True)
    artists = db.relationship('Artist', backref='city', lazy=True)

    @property
    def num_upcoming_shows(self):
        upcoming_shows = 0
        for venue in self.venues:
            upcoming_shows += venue.num_upcoming_shows
        return upcoming_shows

    @property
    def serialized_venues(self):
        ordered_venues = order_by_num_upcoming_shows(self.venues)
        return {
            'city': self.name,
            'state': self.state,
            'venues': [venue.serialize_summary for venue in ordered_venues]
        }

    @classmethod
    def get_id(cls, city_name, city_state):
        city_is_known = cls.query.filter(cls.name == city_name, cls.state == city_state).one_or_none()
        if city_is_known:
            city_id = city_is_known.id
        else:
            try:
                new_city = cls(name=city_name, state=city_state)
                city_id = new_city.id
                db.session.add(new_city)
                db.session.commit()
            except:
                print(sys.exc_info())
                city_id = None
            finally:
                db.session.close()
        return city_id


#    ----------------------------------------------------------------------------#
# Filters.
#    ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateparser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en_US')


app.jinja_env.filters['datetime'] = format_datetime


def order_by_num_upcoming_shows(input_list):
    ordered_list = []
    max_num = 0
    min_num = 0
    for item in input_list:
        if item.num_upcoming_shows >= max_num:
            max_num = item.num_upcoming_shows
            ordered_list = [item] + ordered_list
        elif item.num_upcoming_shows <= min_num:
            min_num = item.num_upcoming_shows
            ordered_list = ordered_list + [item]
        else:
            i = 0
            for ordered_item in ordered_list:
                if item.num_upcoming_shows > ordered_item.num_upcoming_shows:
                    break
                i += 1
            ordered_list.insert(i, item)
    return ordered_list


def search_model_for_names_insensitive(model, search_term):
    search = "%{}%".format(search_term)
    matches = model.query.filter(model.name.ilike(search))
    return {
        "count": matches.count(),
        "data": [match.serialize_summary for match in matches]
    }


def format_phone_number(phone_number):
    number = ''.join(re.split('\.|-', phone_number))
    return f'{number[:3]}-{number[3:6]}-{number[6:]}'


def format_genres(data):
    genres = data.get('genres')
    if isinstance(genres, list):
        genres = ','.join(genres)
    return genres

#    ----------------------------------------------------------------------------#
# Controllers.
#    ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#    Venues
#    ----------------------------------------------------------------

@app.route('/venues')
def venues():
    cities = order_by_num_upcoming_shows( City.query.all() )
    data = [city.serialized_venues for city in cities]
    prints = json.dumps(data, indent=4)
    print(prints)
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    response = search_model_for_names_insensitive(model=Venue, search_term=search_term)
    print(json.dumps(response, indent=4))
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        data = venue.dictionary
        print(json.dumps(data, indent=4))
        return render_template('pages/show_venue.html', venue=data)
    else:
        return abort(404)

#    Create Venue
#    ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    # on successful db insert, flash success
    form = VenueForm(request.form)
    # enum fix pattern: https://stackoverflow.com/questions/13558345/flask-app-using-wtforms-with-selectmultiplefield
    if form.validate_on_submit():
        data = request.form
        city_name = data.get('city')
        city_state = data.get('state')
        name = data.get('name')
        genres = format_genres(data)
        address = data.get('address')
        phone = format_phone_number(data.get('phone'))
        facebook_link = data.get('facebook_link')
        image_link = data.get('image_link')

        try:
            city_id = City.get_id(city_state=city_state, city_name=city_name)
            if city_id is None:
                error = True
            new_venue = Venue(name=name, city_id=city_id, genres=genres, address=address, phone=phone,
                              facebook_link=facebook_link, image_link=image_link)
            db.session.add(new_venue)
            db.session.flush()
            venue_id = new_venue.id
            db.session.commit()
            flash('Venue ' + name + ' was successfully listed!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            error = True
        finally:
            db.session.close()
    else:
        error = True

    if error:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        return abort(500)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    success = False
    try:
        venue = Venue.query.get(venue_id)
        name = venue.name
        if venue:
            for show in venue.shows:
                db.session.delete(show)
            db.session.delete(venue)
            db.session.commit()
            success = True
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if success:
        flash('Venue ' + name + ' successfully deleted.')
        url = url_for('venues')
    else:
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
        url = url_for('show_venue', venue_id=venue_id)
    data = {
        'success': success,
        'url': url
    }
    print(json.dumps(data, indent=4))
    return jsonify({
        'success': success,
        'url': url
    })

#    Artists
#    ----------------------------------------------------------------


@app.route('/artists')
def artists():
    all_artists = Artist.query.all()
    data = [artist.serialize_minimal for artist in all_artists]
    print(json.dumps(data, indent=4))
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    response = search_model_for_names_insensitive(model=Artist, search_term=search_term)
    print(json.dumps(response, indent=4))
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if isinstance(artist, Artist):
        data = artist.dictionary
        print(json.dumps(data, indent=4))
        return render_template('pages/show_artist.html', artist=data)
    else:
        return abort(404)


#    Update
#    ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    if isinstance(artist, Artist):
        data = artist.dictionary
        print(json.dumps(data, indent=4))
        return render_template('forms/edit_artist.html', form=form, artist=data)
    else:
        return abort(404)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)  # fix to get all selected values from form.
    error = False
    data = request.form
    print(json.dumps(data, indent=4))
    if form.validate_on_submit():
        city_name = data.get('city')
        city_state = data.get('state')
        city_id = City.get_id(city_state=city_state, city_name=city_name)
        if city_id is None:
            error = True

        name = data.get('name')
        genres = format_genres(data)
        phone = data.get('phone')
        facebook_link = data.get('facebook_link')
        image_link = data.get('image_link')
        website = data.get('website')
        seeking_venue = True if data.get('seeking_venue') else False
        seeking_description = data.get('seeking_description')
        try:
            artist = Artists.query.get(artist_id)
            artist.name = name
            artist.city_id = city_id
            artist.genres = genres
            artist.phone = phone
            artist.image_link = image_link
            artist.website = website
            artist.facebook_link = facebook_link
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description
            db.session.commit()
            flash('Artist ' + name + ' was successfully updated!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' + name + ' could not be updated.')
            error = True
        finally:
            db.session.close()
    else:
        error = True

    if error:
        return abort(500)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if isinstance(venue, Venue):
        data = venue.dictionary
        form.name.default = data.get('name')
        form.city.default = data.get('city')
        form.state.default = data.get('state', 'AL')
        form.address.default = data.get('address')
        form.phone.default = data.get('phone')
        form.image_link.default = data.get('image_link')
        form.genres.default = data.get('genres', [])
        form.facebook_link.default = data.get('facebook_link')
        form.website.default = data.get('website')
        form.seeking_talent.default = data.get('seeking_talent')
        form.seeking_description.default = data.get('seeking_description')
        form.process()
        print(json.dumps(data, indent=4))
        return render_template('forms/edit_venue.html', form=form, venue=data)
    else:
        return abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)  # fix to get all selected values from form.
    data = request.form
    error = False
    print(json.dumps(data, indent=4))
    if form.validate_on_submit():
        # Get City info
        city_name = data.get('city')
        city_state = data.get('state', 'AL')
        city_id = City.get_id(city_state=city_state, city_name=city_name)
        if city_id is None:
            error = True

        # Get other fields
        name = data.get('name')
        address = data.get('address')
        phone = format_phone_number(data.get('phone'))
        image_link = data.get('image_link')
        genres = format_genres(data)
        facebook_link = data.get('facebook_link')
        website = data.get('website')
        seeking_talent = True if data.get('seeking_talent') else False
        seeking_description = data.get('seeking_description')

        try:
            venue = Venue.query.get(venue_id)
            venue.name = name
            venue.city_id = city_id
            venue.address = address
            venue.phone = phone
            venue.image_link = image_link
            venue.genres = genres
            venue.facebook_link = facebook_link
            venue.website = website
            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description
            db.session.commit()
            flash('Venue ' + name + ' was successfully updated!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' + name + ' could not be updated.')
            error = True
        finally:
            db.session.close()
    else:
        error = True

    if error:
        return abort(500)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))


#    Create Artist
#    ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm(request.form)

    if form.validate_on_submit():
        data = request.form
        city_name = data.get('city')
        city_state = data.get('state')

        name = data.get('name')
        genres = format_genres(data)
        phone = format_phone_number(data.get('phone'))
        image_link = data.get('image_link')
        facebook_link = data.get('facebook_link')
        website = data.get('website')
        seeking_venue = True if data.get('seeking_venue') else False
        seeking_description = data.get('seeking_description')

        try:
            city_id = City.get_id(city_state=city_state, city_name=city_name)
            if city_id is None:
                error = True
            new_artist = Artist(name=name,
                                city_id=city_id,
                                genres=genres,
                                phone=phone,
                                image_link=image_link,
                                facebook_link=facebook_link,
                                website=website,
                                seeking_venue=seeking_venue,
                                seeking_description=seeking_description)
            db.session.add(new_artist)
            db.session.flush()
            artist_id = new_artist.id
            db.session.commit()
            flash('Artist ' + new_artist.name + ' was successfully listed!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            error = True
        finally:
            db.session.close()
    else:
        error = True

    if error:
        flash('An error occurred. Artist ' + name + ' could not be listed.')
        return abort(500)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


#    Shows
#    ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #             num_shows should be aggregated based on number of upcoming shows per venue.
    data=[{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
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

    # on successful db insert, flash success
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

#    ----------------------------------------------------------------------------#
# Launch.
#    ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
        app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
'''
