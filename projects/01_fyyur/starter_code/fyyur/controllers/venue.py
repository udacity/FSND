import sys
from fyyur import app, db
from fyyur.forms import *
from fyyur.models.venue import Venue
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

    print(data[0]['venues'])

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data = Venue.query.get(venue_id)

    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #                    venue_id, [data1, data2, data3]))[0]
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
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')

    venue = Venue(
        name=name, city=city, state=state, address=address,
        phone=phone, image_link=image_link, facebook_link=facebook_link, website_link=website_link)

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
        return render_template('pages/home.html')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              Venue.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))