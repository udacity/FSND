# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import VenueForm, ShowForm, ArtistForm
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY
import sys
from sqlalchemy import and_, func, text, desc, or_

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    created_at = db.Column(db.DateTime, default=datetime.now())
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(ARRAY(db.String(120)), nullable=False, default='[]')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    shows = db.relationship(
      'Show', backref='venue', cascade="all, delete, delete-orphan")


class Artist(db.Model):
    __tablename__ = 'Artist'

    created_at = db.Column(db.DateTime, default=datetime.now())
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(ARRAY(db.String(120)), nullable=False, default='[]')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    shows = db.relationship(
      'Show', backref='artist', cascade="all, delete, delete-orphan")


class Show(db.Model):
    __tablename__ = 'Show'
    __table_args__ = (
      db.UniqueConstraint(
        'artist_id', 'start_time', name='artist_availability'),
      db.UniqueConstraint('venue_id', 'start_time', name='venue_availability')
    )

    created_at = db.Column(db.DateTime, default=datetime.now)
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    artist_id = db.Column(
      db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)


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
    recent_listings = {
        "venues": db.session.query(Venue.id, Venue.name)
        .order_by(desc(Venue.created_at)).limit(10).all(),
        "artists": db.session.query(Artist.id, Artist.name)
        .order_by(desc(Artist.created_at)).limit(10).all()
    }
    return render_template('pages/home.html', recent_listings=recent_listings)


#  Venues
#  ----------------------------------------------------------------


def getFormatedVenueData(filterQuery):
    upcomingShow = func.count(
        text('CASE WHEN "Show".start_time > :date THEN "Show".venue_id END')
        ).params(date=datetime.now())
    venueRows = Venue.query.with_entities(
      Venue.id, Venue.name, upcomingShow.label('num_upcoming_shows')).filter(
        filterQuery).outerjoin(Show).group_by(Venue.id)
    return [venue._asdict() for venue in venueRows]


@app.route('/venues')
def venues():
    data = []
    uniqueStatesAndCities = Venue.query.with_entities(
      Venue.state, Venue.city).distinct(Venue.state, Venue.city).order_by(
        Venue.state, Venue.city).all()
    for state, city in uniqueStatesAndCities:
        obj = {}
        obj['state'] = state
        obj['city'] = city
        obj['venues'] = getFormatedVenueData(
          and_(Venue.state == state, Venue.city == city))
        data.append(obj)
    return render_template('pages/venues.html', areas=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    venue_id = None
    try:
        data = request.form
        newV = Venue(
            name=data['name'],
            genres=data.getlist('genres'),
            address=data['address'],
            city=data['city'],
            state=data['state'],
            phone=data['phone'],
            website=data['website'],
            facebook_link=data['facebook_link'],
            seeking_talent=data['seeking_talent'] == 'True',
            seeking_description=data['seeking_description'],
            image_link=data['image_link']
        )
        db.session.add(newV)
        db.session.flush()
        venue_id = newV.id
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Error: Venue ' + data['name'] + ' could not be listed.')
        return redirect(url_for('create_venue_form'))
    else:
        # on successful db insert, flash success
        flash('Venue ' + data['name'] + ' was successfully listed!')
        return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue_form(venue_id):
    form = VenueForm()
    return render_template(
      'forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        data = request.form
        venue = Venue.query.get(venue_id)
        venue.name = data['name']
        venue.genres = data.getlist('genres')
        venue.address = data['address']
        venue.city = data['city']
        venue.state = data['state']
        venue.phone = data['phone']
        venue.website = data['website']
        venue.facebook_link = data['facebook_link']
        venue.seeking_talent = data['seeking_talent'] == 'True'
        venue.seeking_description = data['seeking_description']
        venue.image_link = data['image_link']
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Error: Venue ' + data['name'] + ' could not be edited.')
        return redirect(url_for('edit_venue_form'))
    else:
        flash('Venue ' + data['name'] + ' was successfully edited!')
        return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    error = False
    venueName = ''
    try:
        venue = Venue.query.get(venue_id)
        venueName = venue.name
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + venueName + ' was successfully deleted!')
        return redirect(url_for('index'))


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_expr = '%' + search_term + '%'
    venues = getFormatedVenueData(
      or_(Venue.name.ilike(search_expr), Venue.state.ilike(
        search_expr), Venue.city.ilike(search_expr)))
    response = {
        "count": len(venues),
        "data": venues
    }
    return render_template(
      'pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    currTime = datetime.now()
    upcomingShowCount = func.count(
      text('CASE WHEN "Show".start_time > :date THEN "Show".venue_id END')
      ).params(date=currTime)
    pastShowCount = func.count(
      text('CASE WHEN "Show".start_time < :date THEN "Show".venue_id END')
      ).params(date=currTime)
    venueRow = Venue.query.filter_by(id=venue_id).with_entities(
      Venue.id, Venue.name, Venue.genres, Venue.address,
      Venue.city, Venue.state, Venue.phone, Venue.website, Venue.facebook_link,
      Venue.seeking_talent, Venue.image_link, upcomingShowCount.label(
        'upcoming_shows_count'), pastShowCount.label('past_shows_count')
        ).outerjoin(Show).group_by(Venue.id)
    shows = db.session.query(func.to_char(
      Show.start_time, "yyyy-mm-ddThh24:mi:ss.msZ").label(
        'start_time'), Artist.id.label('artist_id'), Artist.name.label(
          'artist_name'), Artist.image_link.label('artist_image_link')
          ).filter_by(venue_id=venue_id).join(Artist).group_by(
            Show.start_time, Artist.id)

    venue = {}
    for r in venueRow:
        venue.update(r._asdict())

    venue["past_shows"] = [r._asdict() for r in shows.having(
      Show.start_time < currTime)]
    venue["upcoming_shows"] = [r._asdict() for r in shows.having(
      Show.start_time > currTime)]
    return render_template('pages/show_venue.html', venue=venue)

#  Artists
#  ----------------------------------------------------------------


def getFormatedArtistData(filterQuery):
    upcomingShow = func.count(text(
      'CASE WHEN "Show".start_time > :date THEN "Show".artist_id END')
      ).params(date=datetime.now())
    artistRows = Artist.query.with_entities(
        Artist.id, Artist.name, upcomingShow.label('num_upcoming_shows')
        ).filter(filterQuery).outerjoin(Show).group_by(Artist.id)
    return [artist._asdict() for artist in artistRows]


@app.route('/artists')
def artists():
    return render_template(
      'pages/artists.html', artists=Artist.query.with_entities(
        Artist.id, Artist.name).all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_expr = '%' + search_term + '%'
    artists = getFormatedArtistData(
      or_(Artist.name.ilike(search_expr), Artist.state.ilike(
        search_expr), Artist.city.ilike(search_expr)))
    response = {
        "count": len(artists),
        "data": artists
    }
    return render_template(
      'pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    currTime = datetime.now()
    upcomingShowCount = func.count(
      text('CASE WHEN "Show".start_time > :date THEN "Show".artist_id END')
      ).params(date=currTime)
    pastShowCount = func.count(text(
      'CASE WHEN "Show".start_time < :date THEN "Show".artist_id END')
      ).params(date=currTime)
    artistRow = Artist.query.filter_by(id=artist_id).with_entities(
      Artist.id, Artist.name, Artist.genres, Artist.city, Artist.state,
      Artist.phone, Artist.website, Artist.facebook_link, Artist.seeking_venue,
      Artist.image_link, upcomingShowCount.label('upcoming_shows_count'),
      pastShowCount.label('past_shows_count')).outerjoin(Show).group_by(
        Artist.id)
    shows = db.session.query(func.to_char(
      Show.start_time, "yyyy-mm-ddThh24:mi:ss.msZ").label('start_time'),
      Venue.id.label('venue_id'), Venue.name.label('venue_name'),
      Venue.image_link.label('venue_image_link')).filter_by(
        artist_id=artist_id).join(Venue).group_by(Show.start_time, Venue.id)

    artist = {}
    for r in artistRow:
        artist.update(r._asdict())

    artist["past_shows"] = [r._asdict() for r in shows.having(
      Show.start_time < currTime)]
    artist["upcoming_shows"] = [r._asdict() for r in shows.having(
      Show.start_time > currTime)]

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist_form(artist_id):
    form = ArtistForm()
    return render_template(
      'forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        data = request.form
        artist = Artist.query.get(artist_id)
        artist.name = data['name']
        artist.genres = data.getlist('genres')
        artist.city = data['city']
        artist.state = data['state']
        artist.phone = data['phone']
        artist.website = data['website']
        artist.facebook_link = data['facebook_link']
        artist.seeking_venue = data['seeking_venue'] == 'True'
        artist.seeking_description = data['seeking_description']
        artist.image_link = data['image_link']
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Error: Artist ' + data['name'] + ' could not be edited.')
        return redirect(url_for('edit_artist_form', artist_id=artist_id))
    else:
        flash('Artist ' + data['name'] + ' was successfully edited!')
        return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    artist_id = None
    try:
        data = request.form
        newA = Artist(
          name=data['name'],
          genres=data.getlist('genres'),
          city=data['city'],
          state=data['state'],
          phone=data['phone'],
          website=data['website'],
          facebook_link=data['facebook_link'],
          seeking_venue=data['seeking_venue'] == 'True',
          seeking_description=data['seeking_description'],
          image_link=data['image_link']
        )
        db.session.add(newA)
        db.session.flush()
        artist_id = newA.id
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Error: Artist ' + data['name'] + ' could not be created.')
        return redirect(url_for('create_artist_form'))
    else:
        # on successful db insert, flash success
        flash('Artist ' + data['name'] + ' was successfully created!')
        return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------


@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
    error = False
    artistName = ''
    try:
        artist = Artist.query.get(artist_id)
        artistName = artist.name
        db.session.delete(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + artistName + ' was successfully deleted!')
        return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    showsRow = db.session.query(Show).with_entities(
      func.to_char(Show.start_time, "yyyy-mm-ddThh24:mi:ss.msZ").label(
        'start_time'), Venue.id.label('venue_id'), Venue.name.label(
          'venue_name'), Artist.id.label('artist_id'), Artist.name.label(
            'artist_name'), Artist.image_link.label('artist_image_link'),
          ).join(Venue).join(Artist).order_by(desc(Show.start_time))
    shows = [r._asdict() for r in showsRow]
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        data = request.form
        newS = Show(
            artist_id=data['artist_id'],
            venue_id=data['venue_id'],
            start_time=data['start_time']
        )
        db.session.add(newS)
        db.session.flush()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Error: Show could not be created.')
        return redirect(url_for('create_shows'))
    else:
        flash('Show was successfully created!')
        return redirect(url_for('shows'))


@app.route('/shows/search', methods=['POST'])
def search_shows():
    search_term = request.form.get('search_term', '')
    showsRow = Show.query.with_entities(
      Artist.name.label('artist_name'), Venue.name.label('venue_name'),
      Show.start_time, Show.artist_id, Show.venue_id).filter(
        or_(Artist.name.ilike('%' + search_term + '%'), Venue.name.ilike(
          '%' + search_term + '%'))).join(Artist).join(Venue)
    shows = [r._asdict() for r in showsRow]
    response = {
        "count": len(shows),
        "data": shows
    }
    return render_template(
      'pages/show.html', results=response, search_term=search_term)


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
          '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
          )
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
