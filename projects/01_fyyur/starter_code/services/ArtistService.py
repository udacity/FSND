from datetime import datetime
import sys
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func

from forms import ArtistForm
from models.Artist import Artist
from models.Show import Show
from models.Venue import Venue
from models.shared import db
from utils.Utils import Utils


class ArtistService:

    @staticmethod
    def artists_get():
        artists = Artist.query.all()

        data = []

        for artist in artists:
            data.append({
                "id": artist.id,
                "name": artist.name
            })

        return render_template('pages/artists.html', artists=data)

    @staticmethod
    def artist_search():
        artists = Artist.query.filter(func.lower(Artist.name).contains(func.lower(request.form['search_term']))).all()

        response = {
            "count": len(artists),
            "data": []
        }

        for artist in artists:
            num_of_upcoming_shows = Show.query.filter(Show.venue_id == artist.id).all()
            response["data"].append(Utils.create_search_data(artist.id, artist.name, num_of_upcoming_shows))

        return render_template('pages/search_artists.html', results=response,
                               search_term=request.form.get('search_term', ''))

    @staticmethod
    def artist_get(artist_id):
        artist = Artist.query.filter(Artist.id == artist_id).first()
        artist_shows = db.session.query(Show.start_time.label('start_time'), Venue.id.label('venue_id'),
                                        Venue.name.label('venue_name'),
                                        Venue.image_link.label('venue_image_link')).join(Venue).filter(
            Show.artist_id == artist_id).all()

        past_shows = []
        upcoming_shows = []

        for show in artist_shows:
            show_time = {
                "venue_id": show.venue_id,
                "venue_name": show.venue_name,
                "venue_image_link": show.venue_image_link,
                "start_time": show.start_time
            }
            if Utils.str_to_date(show['start_time']) < datetime.now():
                past_shows.append(show_time)
            else:
                upcoming_shows.append(show_time)

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

        return render_template('pages/show_artist.html', artist=data)

    @staticmethod
    def artist_get_create_form():
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)

    @staticmethod
    def artist_create():
        # called upon submitting the new artist listing form
        # TODO: insert form data as a new Venue record in the db, instead
        # TODO: modify data to be the data object returned from db insertion

        seeking_venue = False
        if request.form.__contains__('seeking_venue'):
            seeking_venue = True
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist(key='genres')
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website_link = request.form['website_link']
        seeking_venue = seeking_venue
        seeking_description = request.form['seeking_description']

        error = False
        try:
            artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link,
                            image_link=image_link, website_link=website_link,
                            seeking_venue=seeking_venue,
                            seeking_description=seeking_description, genres=genres)

            db.session.add(artist)
            db.session.commit()

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            if error:
                flash('An error occurred. Artist ' + name + ' could not be listed.')
            else:
                flash('Artist ' + name + ' was successfully listed!')

        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')

    @staticmethod
    def artist_get_edit_form(artist_id):
        form = ArtistForm()
        found_artist = Artist.query.filter(artist_id == Artist.id).first()
        form.name.default = found_artist.name
        form.city.default = found_artist.city
        form.phone.default = found_artist.phone
        form.state.default = found_artist.state
        form.genres.default = found_artist.genres
        form.facebook_link.default = found_artist.facebook_link
        form.image_link.default = found_artist.image_link
        form.website_link.default = found_artist.website_link
        form.seeking_venue.default = found_artist.seeking_venue
        form.seeking_description.default = found_artist.seeking_description
        form.process()
        artist = {
            "id": found_artist.id,
            "name": found_artist.name,
            "genres": found_artist.genres,
            "city": found_artist.city,
            "state": found_artist.state,
            "phone": found_artist.phone,
            "website": found_artist.website_link,
            "facebook_link": found_artist.facebook_link,
            "seeking_venue": found_artist.seeking_venue,
            "seeking_description": found_artist.seeking_description,
            "image_link": found_artist.image_link
        }
        # TODO: populate form with fields from artist with ID <artist_id>
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    @staticmethod
    def artist_update(artist_id):
        seeking_venue = False
        if ('seeking_venue' in request.form):
            seeking_venue = True

        # TODO: take values from the form submitted, and update existing
        artist = Artist.query.filter(Artist.id == artist_id).first()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist(key='genres')
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website_link = request.form['website_link']
        artist.seeking_venue = seeking_venue
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()

        return redirect(url_for('show_artist', artist_id=artist_id))

    @staticmethod
    def artist_delete(artist_id):
        try:
            Show.query.filter(Show.artist_id == artist_id).delete()
            Artist.query.filter(Artist.id == artist_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())

        finally:
            db.session.close()

        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
        return render_template('pages/home.html')
