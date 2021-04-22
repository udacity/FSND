from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
import sys
from sqlalchemy import func

from forms import VenueForm
from models.Venue import Venue
from models.Artist import Artist
from models.Show import Show
from utils.Utils import Utils
from models.shared import db


class VenueService:

    def format_datetime(value, format='medium'):
        date = dateutil.parser.parse(value)
        if format == 'full':
            format = "EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
            format = "EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format, locale='en')

    @staticmethod
    def venues_get():
        venues = Venue.query.order_by(Venue.city).all()

        def create_venue_data(city, state):
            return {
                "city": city,
                "state": state,
                "venues": []
            }

        current_state = None
        current_city = None
        current_venue_data = None
        data = []

        for venue in venues:

            venue_shows = Show.query.filter(Show.venue_id == venue.id)
            upcoming_shows = 0
            for show in venue_shows:
                if Utils.str_to_date(show.start_time) > datetime.now():
                    upcoming_shows += 1

            def create_venue(id, name, num_upcoming_shows):
                return {
                    "id": id,
                    "name": name,
                    "num_upcoming_shows": num_upcoming_shows
                }

            if current_city != venue.city or current_state != venue.state:
                if current_venue_data:
                    data.append(current_venue_data)

                current_city = venue.city
                current_state = venue.state
                current_venue_data = create_venue_data(venue.city, venue.state)
                current_venue_data['venues'].append(create_venue(venue.id, venue.name, upcoming_shows))
            else:
                current_venue_data['venues'].append(create_venue(venue.id, venue.name, upcoming_shows))
        else:
            if current_venue_data:
                data.append(current_venue_data)

        return render_template('pages/venues.html', areas=data)

    @staticmethod
    def venue_search():
        venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(request.form['search_term']))).all()

        response = {
            "count": len(venues),
            "data": []
        }

        for venue in venues:
            num_of_upcoming_shows = Show.query.filter(Show.venue_id == venue.id).all()
            response["data"].append(Utils.create_search_data(venue.id, venue.name, num_of_upcoming_shows))

        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))

    @staticmethod
    def venue_get(venue_id):
        venue = Venue.query.filter(Venue.id == venue_id).first()
        venue_shows = db.session.query(Show.start_time.label('start_time'), Artist.id.label('artist_id'),
                                       Artist.name.label('artist_name'),
                                       Artist.image_link.label('artist_image_link')).join(
            Artist).filter(Show.venue_id == venue_id).all()

        past_shows = []
        upcoming_shows = []

        for show in venue_shows:
            show_time = {
                "artist_id": show.artist_id,
                "artist_name": show.artist_name,
                "artist_image_link": show.artist_image_link,
                "start_time": show.start_time
            }
            if Utils.str_to_date(show['start_time']) < datetime.now():
                past_shows.append(show_time)
            else:
                upcoming_shows.append(show_time)

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

        return render_template('pages/show_venue.html', venue=data)

    @staticmethod
    def venue_get_create_form():
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)

    @staticmethod
    def venue_create():
        seeking_talent = False
        if request.form.__contains__('seeking_talent'):
            seeking_talent = True
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist(key='genres')
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website_link = request.form['website_link']
        seeking_talent = seeking_talent
        seeking_description = request.form['seeking_description']

        error = False
        try:
            venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
                          facebook_link=facebook_link, image_link=image_link, website_link=website_link,
                          seeking_talent=seeking_talent, seeking_description=seeking_description, genres=genres)

            db.session.add(venue)
            db.session.commit()

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            if error:
                flash('An error occurred. Venue ' + name + ' could not be listed.')
            else:
                flash('Venue ' + name + ' was successfully listed!')

        return render_template('pages/home.html')


    @staticmethod
    def venue_get_edit_form(venue_id):
        form = VenueForm()
        found_venue = Venue.query.filter(venue_id == Venue.id).first()
        form.name.default = found_venue.name
        form.city.default = found_venue.city
        form.address.default = found_venue.address
        form.phone.default = found_venue.phone
        form.state.default = found_venue.state
        form.genres.default = found_venue.genres
        form.facebook_link.default = found_venue.facebook_link
        form.image_link.default = found_venue.image_link
        form.website_link.default = found_venue.website_link
        form.seeking_talent.default = found_venue.seeking_talent
        form.seeking_description.default = found_venue.seeking_description
        form.process()
        venue = {
            "id": found_venue.id,
            "name": found_venue.name,
            "genres": found_venue.genres,
            "address": found_venue.address,
            "city": found_venue.city,
            "state": found_venue.state,
            "phone": found_venue.state,
            "website": found_venue.website_link,
            "facebook_link": found_venue.facebook_link,
            "seeking_talent": found_venue.seeking_talent,
            "seeking_description": found_venue.seeking_description,
            "image_link": found_venue.image_link
        }
        # TODO: populate form with values from venue with ID <venue_id>
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    @staticmethod
    def venue_update(venue_id):
        seeking_talent = False
        if ('seeking_talent' in request.form):
            seeking_talent = True

        venue = Venue.query.filter(Venue.id == venue_id).first()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist(key='genres')
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        venue.website_link = request.form['website_link']
        venue.seeking_talent = seeking_talent
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()

        return redirect(url_for('show_venue', venue_id=venue_id))

    @staticmethod
    def venue_delete(venue_id):
        try:
            Show.query.filter(Show.venue_id == venue_id).delete()
            Venue.query.filter(Venue.id == venue_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
            print(sys.exc_info())

        finally:
            db.session.close()

        return render_template('pages/home.html')