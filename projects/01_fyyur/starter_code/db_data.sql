--Insert venues
INSERT INTO "Venue" 
("name", city, "state", "address", phone, image_link, facebook_link, genres, seeking_talent, seeking_description, website) 
values ('The Musical Hop','San Francisco','CA','1015 Folsom Street','123-123-1234','https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60','https://www.facebook.com/TheMusicalHop',
'Jazz, Reggae, Swing, Classical, Folk', True, 'We are on the lookout for a local artist to play every two weeks. Please call us.','https://www.themusicalhop.com');

INSERT INTO "Venue" 
("name", city, "state", "address", phone, image_link, facebook_link, genres, seeking_talent, seeking_description, website) 
values ('The Dueling Pianos Bar','New York','NY','335 Delancey Street','914-003-1132','https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80','https://www.facebook.com/theduelingpianos',
'Classical, R&B, Hip-Hop', False,'','https://www.theduelingpianos.com' );

  INSERT INTO "Venue" 
("name", city, "state", "address", phone, image_link, facebook_link, genres, seeking_talent, website)  
values ( 'Park Square Live Music & Coffee','San Francisco','CA','34 Whiskey Moore Ave','415-000-1234','https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80','https://www.facebook.com/ParkSquareLiveMusicAndCoffee',
'Rock n Roll, Jazz, Classical, Folk', False,'https://www.parksquarelivemusicandcoffee.com');


--Insert Artist
INSERT INTO "Artist"
("name",genres,city, "state", phone, website, facebook_link, seeking_venue, seeking_description, image_link )
values
('Guns N Petals','Rock n Roll','San Francisco','CA','326-123-5000','https://www.gunsnpetalsband.com','https://www.facebook.com/GunsNPetals',
 True,'Looking for shows to perform at in the San Francisco Bay Area!','https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80')
INSERT INTO "Artist"
("name",genres,city, "state", phone, website, facebook_link, seeking_venue, seeking_description, image_link )
values
('Guns N Petals','Rock n Roll','San Francisco','CA','326-123-5000','https://www.gunsnpetalsband.com','https://www.facebook.com/GunsNPetals',
 True,'Looking for shows to perform at in the San Francisco Bay Area!','https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80');
INSERT INTO "Artist"
("name",genres,city, "state", phone, website, facebook_link, seeking_venue, seeking_description, image_link )
values
('Guns N Petals','Rock n Roll','San Francisco','CA','326-123-5000','https://www.gunsnpetalsband.com','https://www.facebook.com/GunsNPetals',
 True,'Looking for shows to perform at in the San Francisco Bay Area!','https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80');
DELETE FROM "Artist";
--As we want to have id 4 we need to insert3 and delete
INSERT INTO "Artist"
("name",genres,city, "state", phone, website, facebook_link, seeking_venue, seeking_description, image_link )
values
('Guns N Petals','Rock n Roll','San Francisco','CA','326-123-5000','https://www.gunsnpetalsband.com','https://www.facebook.com/GunsNPetals',
 True,'Looking for shows to perform at in the San Francisco Bay Area!','https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80');

INSERT INTO "Artist"
("name",genres,city, "state", phone, website, facebook_link, seeking_venue, seeking_description, image_link )
values
('Matt Quevedo','Jazz','New York','NY','300-400-5000','','https://www.facebook.com/mattquevedo923251523',
False, '','https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80');

INSERT INTO "Artist"
("name",genres,city, "state", phone, website, facebook_link, seeking_venue, seeking_description, image_link )
values
('The Wild Sax Band','Jazz, Classical','San Francisco','CA','432-325-5432','','',False,'','https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80');


  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }