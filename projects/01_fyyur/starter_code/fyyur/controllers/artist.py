import sys
from fyyur import app, db
from fyyur.forms import *
from datetime import datetime
from sqlalchemy import cast, DATE, func
from fyyur.models.show import Show
from fyyur.models.venue import Venue
from fyyur.models.artist import Artist
from flask import Flask, render_template, request, Response, flash, redirect, url_for


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    facebook_link = request.form.get('facebook_link', '')
    genres = request.form.get('genres', '')
    website_link = request.form.get('website_link', '')
    seeking_venue = eval(request.form.get('seeking_venue', ''))
    seeking_description = request.form.get('seeking_description', '')

    if not seeking_venue:
        seeking_description = ''

    artist = Artist(name=name, city=city, state=state,
                    phone=phone, facebook_link=facebook_link,
                    genres=genres, seeking_venue=seeking_venue,
                    seeking_description=seeking_description,
                    website_link=website_link)

    error = False

    try:
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

        if not error:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
            return redirect(url_for('artists'))
        else:
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  artist.name + ' could not be listed.')


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search = "%{}%".format(search_term)

    artists = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(search)).all()

    response = {
        "count": len(artists),
        "data": []
    }

    for artist in artists:
        upcoming_shows = Show.query.filter(
            cast(Show.start_time, DATE) > datetime.now(),
            Show.artist_id == artist.id
        ).count()

        response['data'].append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': upcoming_shows
        })

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)
    genres = []

    if artist.genres:
        genres = artist.genres.split(',')

    past_shows = Show.query.join(Venue).filter(
        cast(Show.start_time, DATE) < datetime.now(),
        Show.artist_id == artist_id
    ).all()

    upcoming_shows = Show.query.join(Venue).filter(
        cast(Show.start_time, DATE) > datetime.now(),
        Show.artist_id == artist_id
    ).all()


    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "genres": genres,
        "facebook_link": artist.facebook_link,
        "website_link": artist.website_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
   
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    artist = Artist.query.get(artist_id)

    genres = []
    if len(artist.genres) > 0:
        genres = artist.genres.split(',')

    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        facebook_link=artist.facebook_link,
        website_link=artist.website_link,
        image_link=artist.image_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description,
    )

    form.genres.data = genres

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    genres = request.form.getlist('genres')
    seeking_venue = eval(request.form.get('seeking_venue', ''))
    seeking_description = request.form.get('seeking_description', '')
    image_link = request.form.get('image_link', '')

    artist = Artist.query.get(artist_id)

    if not seeking_venue:
        seeking_description = ''

    if genres:
        genres = ','.join(genres)
    else:
        genres = []

    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.website_link = website_link
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.image_link = image_link

    error = False

    try:
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash('An error occurred. Artist ' +
              artist.name + ' could not be edited.')
