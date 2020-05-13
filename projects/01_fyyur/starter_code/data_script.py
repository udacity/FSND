from app import Venue, Artist, Show, db
#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

#insert into venue values (1, 'Volksfest', 'Straubing', 'CA', '1015 Folsom Street', '123-123-1234', 'test.jpg', 'www.facebook.com', 'test beschreibung', True, 'www.test.de', ARRAY ['Jazz', 'Swing']);
#insert into venue values (2, 'The Musical Hop', 'San Francisco', 'CA', '1015 Folsom Street', '123-123-1234', 'test1.jpg', 'www.facebook.com', 'test1 beschreibung', True, 'www.test.de', ARRAY ['Classical', 'Folk']);
#insert into venue values (3, 'The Dueling Pianos Bar', 'New York', 'NY', '335 Delancey Street"', '914-003-1132', 'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80', 'www.facebook.com', 'test2 beschreibung', True, 'www.test.de', ARRAY ['R&B', 'Classical']);

venues_data = [{
    "id": 1,
    "city": "San Francisco",
    "state": "CA",
    "name": "The Musical Hop",
    "address": "1015 Folsom Street",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
}, {
    "id": 3,
    "city": "San Francisco",
    "state": "CA",
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "seeking_description": None,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
}, {
    "id": 2,
    "city": "New York",
    "state": "NY",
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "seeking_description": None,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
}]

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

#insert into artist values (4, 'Guns N Petals', 'San Francisco', 'CA', '326-123-5000', ARRAY ['Rock n Roll'], 'image_test.jpg', 'www.facebook.de', True, 'seeking description', 'www.test_url.de');
#insert into artist values (5, 'Matt Quevedo', 'New York', 'NY', '300-400-5000', ARRAY ['Jazz'], 'image_test5.jpg', 'www.facebook.de', True, 'seeking description 5', 'www.test_url5.de');
#insert into artist values (6, 'The Wild Sax Band', 'San Francisco', 'CA', '432-325-5432', ARRAY ['Jazz', 'Classical'], 'image_test6.jpg', 'www.facebook.de', True, 'seeking description 6', 'www.test_url6.de');

artists_data = [{
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }, {
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "seeking_description": None,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"
    }, {
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "seeking_description": None,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
}]

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------
shows_data = [{
    "venue_id": 1,
    "artist_id": 4,
    "start_time": "2019-05-21T21:30:00.000Z"
    }, {
    "venue_id": 3,
    "artist_id": 5,
    "start_time": "2019-06-15T23:00:00.000Z"
    }, {
    "venue_id": 3,
    "artist_id": 6,
    "start_time": "2035-04-01T20:00:00.000Z"
    }, {
    "venue_id": 3,
    "artist_id": 6,
    "start_time": "2035-04-08T20:00:00.000Z"
    }, {
    "venue_id": 3,
    "artist_id": 6,
    "start_time": "2035-04-15T20:00:00.000Z"
    }]


#  ----------------------------------------------------------------
#  Load Data into DB
#  ----------------------------------------------------------------
for v in venues_data:
    venue = Venue(id=v["id"],
                  name=v["name"])
    for key, value in v.items():
        setattr(venue, key, value)
    db.session.add(venue)
    db.session.commit()

for a in artists_data:
    artist = Artist(id=a["id"],
                    name=a["name"])
    for key, value in a.items():
        setattr(artist, key, value)
    db.session.add(artist)
    db.session.commit()

for s in shows_data:
    show = Show(venue_id=s["venue_id"],
                artist_id=s["artist_id"],
                start_time=s["start_time"])
    db.session.add(show)
    db.session.commit()