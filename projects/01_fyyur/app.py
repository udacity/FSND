# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import sys

import babel
import dateutil.parser
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import itertools
import logging
from logging import FileHandler, Formatter

from forms import ArtistForm, VenueForm, ShowForm
from models import db, Venue, Artist, Show

# ----------------------------------------------------------------------------#
# App init
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object("config")
app.config.from_envvar("APPLICATION_SETTINGS")
migrate = Migrate(app, db)
db.init_app(app)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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

    # get all venues
    venues = Venue.query.all()

    keyfunc = lambda v: (v["city"], v["state"])
    sorted_venues = sorted(venues, key=keyfunc)
    grouped_venues = itertools.groupby(sorted_venues, key=keyfunc)

    data = [
        {"city": key[0], "state": key[1], "venues": list(data)}
        for key, data in grouped_venues
    ]

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # term to search for (eg., 'Superdome')
    search_term = request.form.get("search_term", "")

    search_results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

    # query the db using ilike
    # response = Venue.query.filter(Venue.name.ilike(search_term)).all()
    venues = [
        {
            "id": venue.id,
            "name": venue.name,
            # 'num_upcoming_shows': venue.upcoming_shows_count
        }
        for venue in search_results
    ]

    response = {"count": len(search_results), "data": list(venues)}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):

    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0

    # get venue with all shows AND artists
    venue = Venue.query.get(venue_id)

    # get current time
    now = datetime.now()

    # get upcoming_shows
    for show in venue.show:
        # get artist data
        artist_data = Artist.query.get(show.artist_id)
        if show.start_time > now:
            upcoming_shows_count += 1
            upcoming_shows.append(
                {
                    "artist_id": show.artist_id,
                    "artist_name": artist_data.name,
                    "artist_image_link": artist_data.image_link,
                    "start_time": show.start_time.isoformat(),
                }
            )
        elif show.start_time < now:
            past_shows_count += 1
            past_shows.append(
                {
                    "artist_id": show.artist_id,
                    "artist_name": artist_data.name,
                    "artist_image_link": artist_data.image_link,
                    "start_time": show.start_time.isoformat(),
                }
            )

    data = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
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
    error = False

    try:
        data = Venue(
            name=request.form["name"],
            address=request.form["address"],
            city=request.form["city"],
            state=request.form["state"],
            phone=request.form["phone"],
            genres=request.form["genres"],
            website=request.form["website"],
            image_link=request.form["image_link"],
            facebook_link=request.form["facebook_link"],
            seeking_talent=request.form["seeking_talent"],
            seeking_description=request.form["seeking_description"],
        )
        if data.seeking_talent == "y":
            data.seeking_talent = True
        else:
            data.seeking_talent = False
        db.session.add(data)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
        flash("An error occurred. Venue " + data.name + " could not be listed.")
    else:
        flash("Venue " + request.form["name"] + " was successfully listed!")

    return render_template("pages/home.html")


# delete a show
@app.route("/shows/<show_id>", methods=["DELETE"])
def delete_show(show_id):
    error = False

    show = Show.query.get(show_id)

    try:
        db.session.delete(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
        flash("An error occurred. Show could not be deleted.")
    else:
        flash("Show was successfully deleted!")
        return redirect(url_for("index"))


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False

    venue = Venue.query.get(venue_id)

    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
        flash("An error occurred. Venue could not be deleted.")
    else:
        flash("Venue was successfully deleted!")
        return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # return all artists
    data = Artist.query.all()

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # term to search for (eg., 'guns n petals')
    search_term = request.form.get("search_term", "")

    search_results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    # query the db using ilike
    # response = Venue.query.filter(Venue.name.ilike(search_term)).all()
    artists = [
        {
            "id": artist.id,
            "name": artist.name,
            # 'num_upcoming_shows': venue.upcoming_shows_count
        }
        for artist in search_results
    ]

    response = {"count": len(search_results), "data": list(artists)}

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0

    # get venue with all shows AND artists
    artist = Artist.query.get(artist_id)

    # get current time
    now = datetime.now()

    # get upcoming_shows
    for show in artist.show:
        # get artist data
        venue_data = Venue.query.get(show.venue_id)
        if show.start_time > now:
            upcoming_shows_count += 1
            upcoming_shows.append(
                {
                    "venue_id": show.venue_id,
                    "venue_name": venue_data.name,
                    "venue_image_link": venue_data.image_link,
                    "start_time": show.start_time.isoformat(),
                }
            )
        elif show.start_time < now:
            past_shows_count += 1
            past_shows.append(
                {
                    "venue_id": show.artist_id,
                    "venue_name": venue_data.name,
                    "venue_image_link": venue_data.image_link,
                    "start_time": show.start_time.isoformat(),
                }
            )

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):

    # get artist
    artist = Artist.query.get(artist_id)

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
    }

    form = ArtistForm(data=data)

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # check to make sure the artist exists
    # then update the artist by artist_id
    # error = False

    artist = Artist.query.get(artist_id)

    # get form
    form = ArtistForm(request.form)

    # check if artist exists
    # if artist is None:
    #     abort(404)
    #     flash("artist was not found")

    # validation + request type
    # populate artist w populate_obj
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash("Artist " + request.form["name"] + " was successfully updated!")

    return redirect(url_for("show_artist", artist_id=artist_id))

    # # try to update the record in db
    # try:
    #     db.session.add(artist)
    #     db.session.commit()
    # except:
    #     error = True
    #     db.session.rollback()
    #     print(sys.exc_info())
    # finally:
    #     db.session.close()
    # if error:
    #     abort(400)
    #     flash("An error occurred. Artist " + artist.name + " could not be updated.")
    # else:
    #     flash("Artist " + request.form["name"] + " was successfully updated!")


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):

    venue = Venue.query.get(venue_id)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "image_link": venue.image_link,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
    }

    form = VenueForm(data=data)

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    venue = Venue.query.get(venue_id)

    form = VenueForm(request.form)  # maybe need obj=venue param?

    form.populate_obj(venue)

    db.session.add(venue)
    db.session.commit()
    flash("Venue " + request.form["name"] + " was successfully updated!")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # on successful db insert, flash success
    error = False
    try:
        data = Artist(
            name=request.form["name"],
            phone=request.form["phone"],
            city=request.form["city"],
            state=request.form["state"],
            genres=request.form["genres"],
            image_link=request.form["image_link"],
            facebook_link=request.form["facebook_link"],
            website=request.form["website"],
            seeking_venue=request.form["seeking_venue"],
            seeking_description=request.form["seeking_description"],
        )
        if data.seeking_venue == "y":
            data.seeking_venue = True
        else:
            data.seeking_venue = False
        db.session.add(data)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
        flash("An error occurred. Artist " + data.name + " could not be listed.")
    else:
        flash("Artist " + request.form["name"] + " was successfully listed!")

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    # get all shows
    shows = Show.query.all()

    data = []

    # for each show, get venue and artist data
    for show in shows:

        # get artist data
        artist = Artist.query.get(show.artist_id)

        # get venue data
        venue = Venue.query.get(show.venue_id)

        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.isoformat(),
            }
        )

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    error = False

    try:
        data = Show(
            venue_id=request.form["venue_id"],
            artist_id=request.form["artist_id"],
            start_time=request.form["start_time"],
        )
        db.session.add(data)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
        flash("An error occurred. Show could not be created.")
    else:
        flash("Show was successfully created!")

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
