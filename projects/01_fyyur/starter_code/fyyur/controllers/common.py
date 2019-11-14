from fyyur import app, db
from fyyur.models.artist import Artist
from fyyur.models.venue import Venue
from flask import render_template


@app.route('/')
def index():
    artists = Artist.query.order_by(Artist.id.desc()).limit(10)
    venues = Venue.query.order_by(Venue.id.desc()).limit(10)
    return render_template('pages/home.html', artists=artists, venues=venues)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500