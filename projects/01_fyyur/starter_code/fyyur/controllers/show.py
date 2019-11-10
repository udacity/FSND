import sys
from fyyur import app, db
from fyyur.forms import *
from fyyur.models.show import Show
from fyyur.models.venue import Venue
from fyyur.models.artist import Artist
from flask import Flask, render_template, request, Response, flash, redirect, url_for


@app.route('/shows')
def shows():
    shows = Show.query.join(Venue).join(Artist).with_entities(
        Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time,).all()

    data = []

    for show in shows:
        print(show)
        data.append({
            "venue_id": show[0],
            "venue_name": show[1],
            "artist_id": show[2],
            "artist_name": show[3],
            "artist_image_link": show[4],
            "start_time": show[5]
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    venue_id = request.form.get('venue_id', '')
    artist_id = request.form.get('artist_id', '')
    start_time = request.form.get('start_time', '')

    start_time_formated = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time_formated)

    error = False

    try:
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        data = Show.query.all()
        flash('Show was successfully listed!')
        return redirect(url_for('shows'))
    else:
        flash('An error occurred. Show could not be listed.')
