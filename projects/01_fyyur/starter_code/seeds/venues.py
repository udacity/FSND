from flask_seeder import Seeder
from app import Venue


# All seeders inherit from Seeder
class VenueSeeder(Seeder):
    # run() will be called by Flask-Seeder
    def run(self):
        venue1 = Venue(
            name="The Musical Hop",
            address="1015 Folsom Street",
            city="San Francisco",
            state="CA",
            phone="123-123-1234",
            website="https://www.themusicalhop.com",
            facebook_link="https://www.facebook.com/TheMusicalHop",
            seeking_talent=True,
            seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
            image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
        )
