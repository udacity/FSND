# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship("Show", backref="venue", lazy=True)


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship("Show", backref="artist", lazy=True)


class Show(db.Model):
    __tablename__ = "Shows"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), primary_key=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), primary_key=False)
    start_time = db.Column(db.DateTime)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    areas_query = (
        Venue.query.with_entities(Venue.city, Venue.state)
        .group_by(Venue.city, Venue.state)
        .all()
    )

    upcoming_shows_query = (
        Show.query.with_entities(func.count(Show.id), Show.venue_id)
        .filter(Show.start_time > datetime.now())
        .group_by(Show.venue_id)
        .all()
    )

    upcoming_shows = {}

    for shows in upcoming_shows_query:
        upcoming_shows[shows.venue_id] = shows[0]

    data = []

    for area in areas_query:
        city = area.city
        state = area.state
        area_venues = Venue.query.with_entities(Venue.id, Venue.name).filter(
            Venue.city == city, Venue.state == state
        )

        area_dict = {"city": city, "state": state, "venues": []}

        for venue in area_venues:
            venue_dict = {"id": venue.id, "name": venue.name}
            try:
                venue_dict["num_upcoming_shows"] = upcoming_shows[venue.id]
            except:
                venue_dict["num_upcoming_shows"] = 0

            area_dict["venues"].append(venue_dict)

        data.append(area_dict)

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    search_term = request.form.get("search_term", "")

    venues = (
        Venue.query.with_entities(Venue.id, Venue.name, func.count(Show.id))
        .join(Show)
        .filter(Show.start_time > datetime.now())
        .filter(Venue.name.ilike("%" + search_term + "%"))
        .group_by(Venue.id, Venue.name)
        .all()
    )

    data = []

    for venue in venues:
        venue_dict = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue[2],
        }
        data.append(venue_dict)

    response = {"count": len(data), "data": data}
    return render_template(
        "pages/search_venues.html", results=response, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    shows = (
        Show.query.with_entities(
            Show.id, Show.artist_id, Artist.name, Artist.image_link, Show.start_time
        )
        .join(Artist)
        .filter(Show.venue_id == venue_id)
        .all()
    )

    past_shows_list = []
    upcoming_shows_list = []

    for show in shows:
        show_dict = {
            "artist_id": show.artist_id,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time),
        }

        if show.start_time < datetime.now():
            past_shows_list.append(show_dict)
        elif show.start_time >= datetime.now():
            upcoming_shows_list.append(show_dict)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():

    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]
    address = request.form["address"]
    phone = request.form["phone"]
    genres = request.form.getlist("genres")
    image_link = request.form["image_link"]
    facebook_link = request.form["facebook_link"]
    website = request.form["website_link"]
    if "seeking_talent" in request.form:
        seeking_talent = True
    else:
        seeking_talent = False

    seeking_description = request.form["seeking_description"]
    try:
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
        )
        db.session.add(venue)
        db.session.commit()

        flash("Venue " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        db.session.rollback()
    finally:
        db.session.close()

    return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>/delete", methods=["POST"])
def delete_venue(venue_id):
    if request.method == "POST":
        try:
            venue = Venue.query.get(venue_id)
            db.session.delete(venue)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists_query = Artist.query.with_entities(Artist.id, Artist.name).all()
    data = []

    for artist in artists_query:
        artist_dict = {"id": artist.id, "name": artist.name}
        data.append(artist_dict)
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():

    search_term = request.form.get("search_term", "")

    artists = (
        Artist.query.with_entities(Artist.id, Artist.name, func.count(Show.id))
        .join(Show)
        .filter(Artist.name.ilike("%" + search_term + "%"))
        .filter(Show.start_time > datetime.now())
        .group_by(Artist.id, Artist.name)
        .all()
    )

    data = []

    for artist in artists:
        artist_dict = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist[2],
        }
        data.append(artist_dict)

    response = {"count": len(data), "data": data}

    return render_template(
        "pages/search_artists.html", results=response, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)

    shows = (
        Show.query.with_entities(
            Show.id, Show.venue_id, Venue.name, Venue.image_link, Show.start_time
        )
        .join(Venue)
        .filter(Show.artist_id == artist_id)
        .all()
    )

    past_shows_list = []
    upcoming_shows_list = []

    for show in shows:
        show_dict = {
            "venue_id": show.venue_id,
            "venue_name": show.name,
            "venue_image_link": show.image_link,
            "start_time": str(show.start_time),
        }

        if show.start_time < datetime.now():
            past_shows_list.append(show_dict)
        elif show.start_time >= datetime.now():
            upcoming_shows_list.append(show_dict)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    if artist.seeking_venue == True:
        form.seeking_venue.data = True
    else:
        form.seeking_venue.data = False
    form.seeking_description.data = artist.seeking_description

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data

    if form.seeking_venue.data == True:
        artist.seeking_venue = True
    else:
        artist.seeking_venue = False
    artist.seeking_description = form.seeking_description.data

    db.session.add(artist)
    db.session.commit()

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    if venue.seeking_talent == True:
        form.seeking_talent.data = True
    else:
        form.seeking_talent.data = False
    form.seeking_description.data = venue.seeking_description

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    form = VenueForm()
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.address = form.address.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data

    if form.seeking_talent.data == True:
        venue.seeking_talent = True
    else:
        venue.seeking_talent = False

    venue.seeking_description = form.seeking_description.data

    db.session.add(venue)
    db.session.commit()
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]
    phone = request.form["phone"]
    genres = request.form.getlist("genres")
    facebook_link = request.form["facebook_link"]
    image_link = request.form["image_link"]
    website = request.form["website_link"]
    if "seeking_venue" in request.form:
        seeking_venue = True
    else:
        seeking_venue = False

    seeking_description = request.form["seeking_description"]
    try:
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(artist)
        db.session.commit()

        flash("Artist " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    shows = (
        Show.query.with_entities(
            Show.venue_id,
            Venue.name.label("venue_name"),
            Show.artist_id,
            Artist.name.label("artist_name"),
            Artist.image_link,
            Show.start_time,
        )
        .filter(Show.start_time > datetime.now())
        .all()
    )

    data = []

    for show in shows:
        show_dict = {
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time),
        }

        data.append(show_dict)
        return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    print(request.form)
    venue_id = request.form["venue_id"]
    artist_id = request.form["artist_id"]
    start_time = request.form["start_time"]
    try:
        show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()

        flash("Show was successfully listed!")
    except:
        flash("An error occurred. Show could not be listed.")
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""

