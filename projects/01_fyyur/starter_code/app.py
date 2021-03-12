from datetime import datetime
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
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from forms import (
    ArtistForm,
    VenueForm,
    ShowForm
)
import os
from flask_migrate import Migrate
from typing import List
from psycopg2.errors import UniqueViolation

# App config
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DevelopmentConfig')
app.config.from_envvar("APP_SETTINGS")
db = SQLAlchemy(app)

# DB migrations
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15))
    image_link = db.Column(db.String(250))
    facebook_link = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(100)) 
    genres = db.Column(postgresql.ARRAY(db.String, dimensions=1))
    
    def __repr__(self):
        return f"<Venue id={self.id}  name={self.name}>"
    

artist_shows = db.Table("artist_shows", 
                        db.Column("show_id", db.ForeignKey("show.id"), primary_key=True),
                        db.Column("artist_id", db.ForeignKey("artist.id"), primary_key=True))

venue_shows = db.Table("venue_shows",
                       db.Column("show_id", db.ForeignKey("show.id"), primary_key=True),
                       db.Column("venue_id", db.ForeignKey("venue.id"), primary_key=True))


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    phone = db.Column(db.String(15))
    image_link = db.Column(db.String(250))
    facebook_link = db.Column(db.String(250))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(100))
    genres = db.Column(postgresql.ARRAY(db.String, dimensions=1))

    def __repr__(self):
        return f"<Artist id={self.id}  name={self.name}>"


class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    artist_id = relationship("Artist", 
                             secondary=artist_shows, 
                             backref=db.backref("shows", lazy=True),
                             cascade="all, delete")
    
    venue_id = relationship("Venue",
                            secondary=venue_shows,
                            backref=db.backref("shows", lazy=True),
                            cascade="all, delete")

    def __repr__(self):
        return f"<Show id={self.id}  start_time={self.start_time}>"


# Filters.


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# routes


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues

@app.route('/venues')
def venues():
    locations: List[tuple] = []
    data: List[dict] = []
    
    for v in Venue.query.all():
        if (loc := v.city.lower(), v.state.lower()) not in locations:
            locations.append(loc)
            data.append({
                "city": v.city, "state": v.state, "venues": []
            })
        index: int = locations.index(loc)
        shows = v.shows

        data[index]["venues"].append(
            {
                "id": v.id, 
                "name": v.name,
                "num_upcoming_shows": len(
                    [el for el in filter(lambda s: s.start_time > datetime.now(), shows)]
                ) 
            }
        )

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    
    data: List[dict] = []
    search_term = request.form.get("search_term", str())
    
    venues_query_stmt = Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))
    if not len(search_term):
        venues = venues_query_stmt.limit(5).all()
    else:
        venues = venues_query_stmt.all()
         
    for v in venues:
        shows = v.shows
        num_upcoming_shows = len(
            [el for el in filter(lambda s: s.start_time > datetime.now(), shows)]
        )
        data.append(
            {
                "id": v.id, 
                "name": v.name, 
                "num_upcoming_shows": num_upcoming_shows
            }
        )

    return render_template('pages/search_venues.html', 
                           results={"count": venues_query_stmt.count(), "data": data}, 
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    shows = venue.shows
    past_shows = [el for el in filter(lambda s: s.start_time < datetime.now(), shows)]
    upcoming_shows = [el for el in filter(lambda s: s not in past_shows, shows)]    

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.facebook_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [
            {
                "artist_id": el.artist_id[0].id,
                "artist_name": el.artist_id[0].name,
                "artist_image_link": el.artist_id[0].image_link,
                "start_time": datetime.strftime(el.start_time, "%Y-%m-%d %H:%M:%S")
            } for el in filter(lambda s: len(s.artist_id), past_shows)
        ],  
        "upcoming_shows": [
            {
                "artist_id": el.artist_id[0].id,
                "artist_name": el.artist_id[0].name,
                "artist_image_link": el.artist_id[0].image_link,
                "start_time": datetime.strftime(el.start_time, "%Y-%m-%d %H:%M:%S")
            } for el in filter(lambda s: len(s.artist_id), upcoming_shows)
        ],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows) 
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    return render_template('forms/new_venue.html', form=VenueForm())


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    venue_name: str = " ".join([el.capitalize() for el in request.form.get("name").split(sep=" ")])
    
    venue = Venue(name=venue_name,
                  city=request.form.get("city"),
                  state=request.form.get("state"),
                  address=request.form.get("address"),
                  facebook_link=request.form.get("facebook_link"),
                  genres=request.form.getlist("genres"),
                  seeking_description=request.form.get("seeking_description"))

    venue.image_link = "/static/img/rock1968.jfif" if venue.image_link is None else venue.image_link
    try:
        db.session.add(venue)
        db.session.commit()
        flash(f"Venue {venue.name} was successfully listed!")
    
    except UniqueViolation:
        db.rollback()
        flash(f"Error: Venue {venue_name} has already been registered")
    
    except Exception as e:
        logging.warning(e.args)
        db.session.rollback()
        flash(f"An error occurred. Venue {venue.name} could not be listed.")
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
        
    try:
        venue = Venue.query.get(venue_id)
        if venue is not None:
            db.session.delete(venue)
            db.session.commit()
            return redirect(url_for('venues'))
        else:
            flash(f"Venue with id {venue_id} not found.")
            return redirect(url_for('venues'))
    except Exception as e:
        logging.warning(e.args)
        db.session.rollback()
        return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data: List[dict] = [{"id": el.id, "name": el.name} for el in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    
    response = {"data": []}
    search_term: str = request.form.get("search_term", str())
    
    artists_query_gen: List[db.Model] = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%")
    )
    if not len(search_term):
        artists = artists_query_gen.limit(5).all()
    else:
        artists = artists_query_gen.all()

    response["count"] = len(artists)

    for el in artists:
        shows = el.shows
        response["data"].append(
            {
                "id": el.id,
                "name": el.name,
                "num_upcoming_shows": len(
                    [show for show in filter(lambda s: s.start_time > datetime.now(), shows)]
                ) 
            }
        ) 

    return render_template('pages/search_artists.html', 
                           results=response, 
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    shows = artist.shows
    past_shows, upcoming_shows = list(), list()
    
    for show in shows: 
        if len(show.venue_id): 
            venue = show.venue_id[0]
            show_info = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": datetime.strftime(show.start_time, "%Y-%m-%d %H:%M:%S")
            }
            if show.start_time > datetime.now():
                upcoming_shows.append(show_info)
            else:
                past_shows.append(show_info)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }    
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist_data = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', 
                           form=ArtistForm(obj=artist_data), 
                           artist=artist_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
    artist = Artist.query.get(artist_id)
    if artist:
        artist.name = request.form.get("name", artist.name)
        artist.city = request.form.get("city", artist.city)
        artist.state = request.form.get("phone", artist.phone)
        artist.image_link = request.form.get("image_link", artist.image_link)
        artist.facebook_link = request.form.get("facebook_link", artist.facebook_link)
        artist.seeking_venue = request.form.get("seeking_venue", artist.seeking_venue)
        artist.seeking_description = request.form.get("seeking_description", artist.seeking_description)
        artist.genres = request.form.getlist("genres")       

    try:
        db.session.commit()
    except Exception as e:
        logging.warning(e.args)
        db.session.rollback()

    return redirect(url_for('show_artist', artist_id=artist.id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue_data = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', 
                           form=VenueForm(obj=venue_data), 
                           venue=venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form_data = request.form
    venue = Venue.query.get(venue_id)
    venue.name = form_data.get("name", venue.name)
    venue.genres = form_data.getlist("genres")
    venue.address = form_data.get("address", venue.address)
    venue.city = form_data.get("city", venue.city)
    venue.state = form_data.get("venue_state", venue.state)
    venue.phone = form_data.get("phone", venue.phone)
    venue.facebook_link = form_data.get("facebook_link", venue.facebook_link)
    venue.seeking_talent = form_data.get("seeking_talent", venue.seeking_talent)
    venue.seeking_description = form_data.get("seeking_description", venue.seeking_description)
    venue.image_link = form_data.get("image_link", venue.image_link)

    try:
        db.session.commit()
    except Exception as e:
        logging.warning(e.args)
        db.session.rollback()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    return render_template('forms/new_artist.html', form=ArtistForm())


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    
    artist_name: str = " ".join([el.capitalize() for el in request.form.get("name").split(sep=" ")])
    artist = Artist(name=artist_name,
                    city=request.form.get("city"),
                    state=request.form.get("state"),
                    phone=request.form.get("phone"),
                    genres=request.form.getlist("genres"),
                    facebook_link=request.form.get("facebook_link"),
                    seeking_description=request.form.get("seeking_description"))
    
    artist.image_link = "/static/img/rock1968.jfif" if artist.image_link is None else artist.image_link

    try:
        db.session.add(artist)
        db.session.commit()
        flash(f"Artist {artist_name} was successfully listed!")
    
    except UniqueViolation:
        db.rollback()
        flash(f"error: Artist {artist_name} has been listen already.")
    
    except Exception as e:
        logging.warning(e.args)
        db.session.rollback()
        flash(f"An error occurred. Artist {artist.name} could not be listed.")
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = [show for show in Show.query.all()]
    data = [
        {
            "venue_id": show.venue_id[0].id,
            "venue_name": show.venue_id[0].name,
            "artist_id": show.artist_id[0].id,
            "artist_name": show.artist_id[0].name,
            "artist_image_link": show.artist_id[0].image_link,
            "start_time": datetime.strftime(show.start_time, "%Y-%m-%d %H:%M:%S")
        } for show in filter(lambda s: len(s.artist_id) and len(s.venue_id), shows)
    ]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    return render_template('forms/new_show.html', form=ShowForm())


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    
    form = {
        "artist_id": request.form.get("artist_id"),
        "venue_id": request.form.get("venue_id"),
        "start_time": request.form.get("start_time")
    }
    try:
        show = Show(start_time=datetime.strptime(form.get("start_time"),
                                                 "%Y-%m-%d %H:%M:%S"))
        
        artist = Artist.query.get(form.get("artist_id"))
        venue = Venue.query.get(form.get("venue_id"))
        db.session.add(show)
        artist.shows = [show]
        venue.shows = [show]
        db.session.commit()    
        flash('Show was successfully listed!')
    except Exception as e:
        logging.warning(e.args)
        db.session.rollback()
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
