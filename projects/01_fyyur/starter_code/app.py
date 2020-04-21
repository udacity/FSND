#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import load_only, selectinload
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

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genres = db.Table(
    'Venue_Genres',
    db.Column(
        'venue_id',
        db.Integer,
        db.ForeignKey('Venue.id', ondelete='CASCADE'),
        primary_key=True),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('Genre.id', ondelete='CASCADE'),
        primary_key=True))

artist_genres = db.Table(
    'Artist_Genres',
    db.Column(
        'artist_id',
        db.Integer,
        db.ForeignKey('Artist.id', ondelete='CASCADE'),
        primary_key=True),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('Genre.id', ondelete='CASCADE'),
        primary_key=True))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(
        db.String,
        nullable=False,
        default='We are looking for local artists to perform at our shows!')

    shows = db.relationship(
        'Show',
        backref='venue',
        passive_deletes=True)

    genres = db.relationship(
        'Genre',
        secondary=venue_genres,
        backref='venue',
        passive_deletes=True)

    UniqueConstraint('name', 'city', 'state', 'address')

    def __repr__(self):
        return f'<Venue id: {self.id}, name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(
        db.String,
        nullable=False,
        default='Looking for shows to perform at!')

    shows = db.relationship(
        'Show',
        backref='artist',
        passive_deletes=True)

    genres = db.relationship(
        'Genre',
        secondary=artist_genres,
        backref='artist',
        passive_deletes=True)

    def __repr__(self):
        return f'<Artist id: {self.id}, name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    venue_id = db.Column(
        db.Integer,
        db.ForeignKey('Venue.id', ondelete='CASCADE'),
        nullable=False)

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id', ondelete='CASCADE'),
        nullable=False)

    def __repr__(self):
        return f'<Show id: {self.id}, venue id: {self.venue_id}, artist id: {self.artist_id}>'


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f'<Genre id: {self.id}, name: {self.name}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(value, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#


def get_genre_choices():
    ''' Returns a list of WTForm Select Field choice values for the genre field'''
    return [(genre.id, genre.name) for genre in Genre.query.all()]


def format_form_label(field_label):
    return ' '.join([word.capitalize() for word in field_label.split('_')])


def flash_invalid_form_errors(form):
    if 'csrf_token' in form.errors:
        csrf_message = form.errors.get('csrf_token')[0]
        message = csrf_message + ' Please try submitting the form again.'
        flash(message=message, category='error')

    for field_label, messages in form.errors.items():
        if field_label == 'csrf_token':
            pass
        else:
            formatted_label = format_form_label(field_label)
            errors = ', '.join(messages)
            message = f'{formatted_label} contains bad input: {errors}'
            flash(message=message, category='warning')

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
    venues = db.session.query(Venue).\
        options(
            load_only('id', 'name', 'city', 'state')).\
        all()

    upcoming_shows = db.session.query(Show).\
        filter(Show.start_time >= datetime.utcnow()).\
        options(load_only('id', 'venue_id')).\
        all()

    show_counts = {}
    for show in upcoming_shows:
        venue_id = show.venue_id
        if venue_id in show_counts:
            show_counts[venue_id] += 1
        else:
            show_counts[venue_id] = 1

    grouped_venues = {}
    for venue in venues:
        location = f'{venue.city},{venue.state}'
        venue_data = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': show_counts.get(venue.id, 0)
        }

        if location not in grouped_venues:
            grouped_venues[location] = {
                'city': venue.city,
                'state': venue.state,
                'venues': [venue_data]
            }
        else:
            grouped_venues[location]['venues'].append(venue_data)

    data = list(grouped_venues.values())
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.\
        filter(Venue.name.ilike(f'%{search_term}%')).\
        all()

    upcoming_shows = db.session.query(Show).\
        filter(
            Show.start_time >= datetime.utcnow(),
            Show.venue_id.in_([venue.id for venue in venues])
    ).\
        options(load_only('id', 'venue_id')).\
        all()

    show_counts = {venue.id: 0 for venue in venues}
    for show in upcoming_shows:
        show_counts[show.venue_id] += 1

    data = []
    for venue in venues:
        venue_data = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': show_counts.get(venue.id, 0)
        }
        data.append(venue_data)

    response = {
        'count': len(venues),
        'data': data
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.\
        filter(Venue.id == venue_id).\
        options(
            selectinload(Venue.genres),
            selectinload(Venue.shows).options(
                selectinload(Show.artist).options(
                    load_only('id', 'name', 'image_link')
                )
            )
        ).\
        one()

    shows = sorted(venue.shows, key=lambda show: show.start_time)
    now = datetime.utcnow()
    past_shows = []
    upcoming_shows = []
    for show in shows:
        start_time = show.start_time.replace(tzinfo=None)
        show_data = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': start_time
        }

        if start_time < now:
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': [genre.name for genre in venue.genres],
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'image_link': venue.image_link,
        'seeking_talent': venue.seeking_talent,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    if venue.seeking_talent:
        data['seeking_description'] = venue.seeking_description

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    form.genres.choices = get_genre_choices()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    form.genres.choices = get_genre_choices()

    if not form.validate():
        flash_invalid_form_errors(form)
        return render_template('forms/new_venue.html', form=form)

    venue = Venue()
    data = form.data
    venue.name = data.get('name')
    venue.address = data.get('address')
    venue.city = data.get('city')
    venue.state = data.get('state')
    venue.phone = data.get('phone')
    venue.image_link = data.get('image_link')
    venue.facebook_link = data.get('facebook_link')
    venue.website = data.get('website')
    venue.seeking_talent = data.get('seeking_talent')
    venue.seeking_description = data.get('seeking_description')

    genre_ids = data.get('genres', [])
    genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
    venue.genres = genres

    try:
        if venue not in db.session.new:
            db.session.add(venue)

        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully listed!')
    except:
        db.session.rollback()
        flash(
            f'An error occurred. Venue {venue.name} could not be listed.',
            category='error')
    finally:
        db.session.close()

    return redirect(url_for('index'))


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
    artists = Artist.query.\
        options(
            load_only('id', 'name')
        ).\
        all()

    data = []
    for artist in artists:
        artist_data = {
            'id': artist.id,
            'name': artist.name
        }
        data.append(artist_data)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.\
        filter(Artist.name.ilike(f'%{search_term}%')).\
        options(
            load_only('id', 'name')
        ).\
        all()

    upcoming_shows = Show.query.\
        filter(
            Show.start_time >= datetime.utcnow(),
            Show.artist_id.in_([artist.id for artist in artists])
        ).\
        options(
            load_only('id', 'artist_id')
        ).\
        all()

    show_counts = {artist.id: 0 for artist in artists}
    for show in upcoming_shows:
        show_counts[show.artist_id] += 1

    data = []
    for artist in artists:
        artist_data = {
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': show_counts.get(artist.id, 0)
        }
        data.append(artist_data)

    response = {
        'count': len(artists),
        'data': data
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.\
        filter(Artist.id == artist_id).\
        options(
            selectinload(Artist.genres),
            selectinload(Artist.shows).options(
                selectinload(Show.artist).options(
                    load_only('id', 'name', 'image_link')
                )
            )
        ).\
        one()

    shows = sorted(artist.shows, key=lambda show: show.start_time)
    now = datetime.utcnow()
    past_shows = []
    upcoming_shows = []
    for show in shows:
        start_time = show.start_time.replace(tzinfo=None)
        show_data = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': start_time
        }

        if start_time < now:
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': [genre.name for genre in artist.genres],
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'image_link': artist.image_link,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'num_past_shows': len(past_shows),
        'num_upcoming_shows': len(upcoming_shows)
    }

    if artist.seeking_venue:
        data['seeking_description'] = artist.seeking_description

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
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
    genres = Genre.query.all()
    form.genres.choices = [(genre.id, genre.name) for genre in genres]
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    form.genres.choices = get_genre_choices()

    if not form.validate():
        flash_invalid_form_errors(form)
        return render_template('forms/new_artist.html', form=form)

    artist = Artist()
    data = form.data
    artist.name = data.get('name')
    artist.city = data.get('city')
    artist.state = data.get('state')
    artist.phone = data.get('phone')
    artist.image_link = data.get('image_link')
    artist.facebook_link = data.get('facebook_link')
    artist.website = data.get('website')
    artist.seeking_venue = data.get('seeking_venue')
    artist.seeking_description = data.get('seeking_description')

    genre_ids = data.get('genres', [])
    genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
    artist.genres = genres

    try:
        if artist not in db.session.new:
            db.session.add(artist)

        db.session.commit()
        flash(f'Artist {artist.name} was successfully listed!')

    except:
        db.session.rollback()
        flash(
            f'An error occurred. Artist {data.name} could not be listed.',
            category='error'
        )
    finally:
        db.session.close()

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.\
        options(
            selectinload(Show.artist).options(
                load_only('name', 'image_link')
            ),
            selectinload(Show.venue).options(
                load_only('name')
            )
        ).\
        all()

    data = []
    for show in shows:
        start_time = show.start_time.replace(tzinfo=None)
        show_data = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': start_time
        }
        data.append(show_data)

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    if not form.validate():
        flash_invalid_form_errors(form)
        return render_template('forms/new_show.html', form=form)

    data = form.data
    show = Show()
    show.artist_id = data.get('artist_id')
    show.venue_id = data.get('venue_id')
    show.start_time = data.get('start_time')

    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash(
            'An error occurred. Show could not be listed.',
            category='error')
    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
