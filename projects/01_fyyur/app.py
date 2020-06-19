#    ----------------------------------------------------------------------------#
# Imports
#    ----------------------------------------------------------------------------#

import json
import sys
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
from flask_wtf import Form
from forms import ShowForm, VenueForm, ArtistForm

#    ----------------------------------------------------------------------------#
# App Config.
#    ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
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
        def serialized(self):
            return {
                'id' : self.id,
                'name' : self.name,
                'genres' : self.genres.split(','),
                'city' : self.city.name,
                'state' : self.city.state,
                'address' : self.address,
                'phone' : self.phone,
                'website' : self.website,
                "facebook_link": self.facebook_link,
                "seeking_talent" : self.seeking_talent,
                "seeking_description": self.seeking_description,
                'image_link' : self.image_link,
                'past_shows' : self.past_shows_serialized,
                'upcoming_shows' : self.upcoming_shows_serialized,
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
        def get_past_shows(self):
            current_time = datetime.datetime.utcnow()
            return db.session.query(Show).filter(Show.start_time < current_time).filter(self.id == Show.artist_id)

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
            'artist_id': self.venue.id,
            'artist_name': self.venue.name,
            'artist_image_link': self.venue.image_link,
            'start_time': self.start_time
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
    search = "%{}%".format(search_term)
    venues = Venue.query.filter(Venue.name.like(search))
    count = venues.count()
    data = [venue.serialize_summary for venue in venues]
    response = {
        "count": venues.count(),
        "data": [venue.serialize_summary for venue in venues]
    }
    print(json.dumps(response, indent=4))
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        data = venue.serialized
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
    data = request.form
    city_name = data.get('city')
    city_state = data.get('state')
    name = data.get('name')
    genres = ','.join(form.genres.data)
    address = data.get('address')
    phone = data.get('phone')
    facebook_link = data.get('facebook_link')
    image_link = data.get('image_link')

    try:
        city_is_known = City.query.filter(City.name == city_name, City.state == city_state).one_or_none()
        if city_is_known:
            city_id = city_is_known.id
        else:
            new_city = City(name=city_name, state=city_state)
            db.session.add(new_city)
            db.session.flush()
            city_id = new_city.id
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
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        error = True
    finally:
        db.session.close()

    if error:
        return abort(400)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    success = True
    try:
        venue = Venue.query.get(venue_id)
        name = venue.name
        if venue:
            db.session.delete(venue)
            db.session.commit()
            success = True
    except:
        db.session.rollback()
        success = False
    finally:
        db.session.close()

    if success:
        flash('Venue ' + name + ' successfully deleted.')
        url = url_for('venues')
    else:
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
        url = url_for('show_venue', venue_id=venue_id)
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
    print(json.dumps(response, indent=4))
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response={
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data1={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [{
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2={
        "id": 5,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "past_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3={
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "past_shows": [],
        "upcoming_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#    Update
#    ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue={
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

#    Create Artist
#    ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


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
