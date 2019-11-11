import sys
from fyyur import app, db
from fyyur.forms import *
from flask import jsonify
from datetime import datetime
from sqlalchemy import cast, DATE
from fyyur.models.venue import Venue
from fyyur.models.show import Show
from flask import Flask, render_template, request, Response, flash, redirect, url_for


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    states = Venue.query.with_entities(
        Venue.city, Venue.state).distinct(Venue.state).all()

    data = []

    for state in states:
        venues = Venue.query.filter_by(state=state.state).all()
        data.append({
            "city": state.city,
            "state": state.state,
            "venues": venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    search = "%{}%".format(search_term)

    venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.like(search)).all()

    response = {
        "count": len(venues),
        "data": []
    }

    for venue in venues:
        upcoming_shows = Show.query.filter(
            cast(Show.start_time, DATE) > datetime.now(),
            Show.venue_id == venue.id
        ).count()

        response['data'].append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': upcoming_shows
        })

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)

    genres = []

    if len(venue.genres) > 0:
        genres = venue.genres.split(',')

    past_shows = Show.query.join(Venue).filter(
        cast(Show.start_time, DATE) < datetime.now(),
        Show.venue_id == venue_id
    ).all()

    upcoming_shows = Show.query.join(Venue).filter(
        cast(Show.start_time, DATE) > datetime.now(),
        Show.venue_id == venue_id
    ).all()

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
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

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('phone', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website = request.form.get('website', '')
    seeking_talent = eval(request.form.get('seeking_talent', ''))
    seeking_description = request.form.get('seeking_description', '')

    venue = Venue(
        name=name, city=city, state=state, address=address,
        phone=phone, image_link=image_link, genres=genres,
        facebook_link=facebook_link, website=website,
        seeking_talent=seeking_talent, seeking_description=seeking_description)

    error = False

    try:
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('venues'))
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              Venue.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get(venue_id)

    error = False
    try:
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        return jsonify({
            'status': 200,
            'message': 'venue deleted succesfuly'
        })
    else:
        return jsonify({
            'status': 400,
            'messgae': 'deletion failed'
        })

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)

    genres = []
    if len(venue.genres) > 0:
        genres = venue.genres.split(',')

    form = VenueForm(
        id=venue.id,
        name=venue.name,
        address=venue.address,
        city=venue.city,
        state=venue.state,
        phone=venue.phone,
        website=venue.website,
        facebook_link=venue.facebook_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description,
        image_link=venue.image_link)

    form.genres.data = genres

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    name = request.form.get('name', '')
    city = request.form.get('city', '')
    address = request.form.get('address', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link', '')
    website = request.form.get('website', '')
    seeking_talent = eval(request.form.get('seeking_talent', ''))
    seeking_description = request.form.get('seeking_description', '')
    image_link = request.form.get('image_link', '')

    venue = Venue.query.get(venue_id)

    if genres:
        genres = ','.join(genres)
    else:
        genres = []

    venue.name = name
    venue.city = city
    venue.state = state
    venue.phone = phone
    venue.address = address
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    venue.image_link = image_link
    venue.website = website

    error = False

    try:
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be edited.')
