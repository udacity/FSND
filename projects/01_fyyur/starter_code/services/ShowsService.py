from flask import render_template, flash, request
import sys
import dateutil.parser
import babel
from forms import ShowForm
from models.Artist import Artist
from models.Show import Show
from models.Venue import Venue
from models.shared import db


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


class ShowsService:

    @staticmethod
    def shows_get():
        shows = db.session.query(Venue.id.label('venue_id'), Venue.name.label('venue_name'),
                                 Artist.id.label("artist_id"),
                                 Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'),
                                 Show.start_time.label('start_time')).join(Show, Artist.id == Show.artist_id) \
            .join(Venue, Venue.id == Show.venue_id).all()

        data = []
        for show in shows:
            data.append({
                "venue_id": show["venue_id"],
                "venue_name": show["venue_name"],
                "artist_id": show["artist_id"],
                "artist_name": show["artist_name"],
                "artist_image_link": show["artist_image_link"],
                "start_time": format_datetime(show["start_time"]),
            })

        return render_template('pages/shows.html', shows=data)

    @staticmethod
    def show_get_create_form():
        form = ShowForm()
        return render_template('forms/new_show.html', form=form)

    @staticmethod
    def show_create():
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        error = False

        try:
            show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

            db.session.add(show)
            db.session.commit()

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        finally:
            db.session.close()
            if error:
                flash('An error occurred. Show could not be listed.')
            else:
                flash('Show was successfully listed!')

        return render_template('pages/home.html')
