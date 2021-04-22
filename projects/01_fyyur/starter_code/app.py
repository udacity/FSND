# ----------------------------------------------------------------------------#
# Imports
from operator import itemgetter

from flask_migrate import Migrate
# ----------------------------------------------------------------------------#

from flask import Flask, render_template
from flask_moment import Moment
from models.shared import db
import logging
from logging import Formatter, FileHandler

from services.ShowsService import ShowsService, format_datetime
from services.VenueService import VenueService
from services.ArtistService import ArtistService
from utils.Utils import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


app.jinja_env.filters['datetime'] = format_datetime


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
    return VenueService.venues_get()


@app.route('/venues/search', methods=['POST'])
def search_venues():
    return VenueService.venue_search()


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    return VenueService.venue_get(venue_id)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    return VenueService.venue_get_create_form()


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    return VenueService.venue_create()


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    return VenueService.venue_delete(venue_id)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    return ArtistService.artists_get()


@app.route('/artists/search', methods=['POST'])
def search_artists():
    return ArtistService.artist_search()


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    return ArtistService.artist_get(artist_id)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    return ArtistService.artist_get_edit_form(artist_id)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    return ArtistService.artist_update(artist_id)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    return VenueService.venue_get_edit_form(venue_id)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    return VenueService.venue_update(venue_id)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    return ArtistService.artist_get_create_form()


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    return ArtistService.artist_create()


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    return ArtistService.artist_delete(artist_id)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    return ShowsService.shows_get()


@app.route('/shows/create')
def create_shows():
    return ShowsService.show_get_create_form()


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    return ShowsService.show_create()


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
