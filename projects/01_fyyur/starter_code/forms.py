from datetime import datetime
from dateutil import tz
import pytz
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Length
import re

genre_list = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Swing', 'Swing'),
    ('Other', 'Other'),
]

state_list = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]


def convert_to_utc(date_time_val, from_tz='America/Chicago', local_format='%Y-%m-%d %H:%M:%S'):
    to_zone = tz.gettz('UTC')
    local_time = datetime.strptime(date_time_val, local_format)
    local_time.replace(tzinfo=tz.gettz(from_tz))
    return local_time.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')


def convert_to_local(utc_val, to_tz='America/Chicago', local_format='%Y-%m-%d %H:%M:%S'):
    to_zone = tz.gettz(to_tz)
    utc_time = datetime.strptime(utc_val, local_format)
    pst = pytz.timezone('UTC')
    utc_time = pst.localize(utc_time)
    return utc_time.astimezone(to_zone)


def validate_phone_number(form, field):
    regex = "\\w{3}-\\w{3}-\\w{4}"
    if not re.search(regex, field.data):
        raise ValidationError('Invalid phone number format')


def validate_choices(form, field, choice_list=None, message=None):
    if choice_list is None:
        choice_list = []
    choice_values = [choice[1] for choice in choice_list]
    for value in field.data:
        if value not in choice_values:
            raise ValidationError(message)


class ValidateGenreChoices(object):
    def __init__(self, message=None):
        if not message:
            message = u'Genre must be in a list of values.'
        self.message = message

    def __call__(self, form, field):
        validate_choices(form, field, genre_list, self.message)


class ValidateStateChoices(object):
    def __init__(self, message=None):
        if not message:
            message = u'State must be in a list of values.'
        self.message = message

    def __call__(self, form, field):
        choice_values = [state[1] for state in state_list]
        if field.data not in choice_values:
            raise ValidationError(self.message)


class ShowForm(Form):

    def set_artist_choice(self, artist_list=None):
        if artist_list is None:
            artist_list = []
        self.artist_id.choices = artist_list

    def set_venue_choice(self, venue_list=None):
        if venue_list is None:
            venue_list = []
        self.venue_id.choices = venue_list

    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
    )
    venue_id = SelectField(
        'venue_id',
        validators=[DataRequired()],
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), ValidateStateChoices()],
        choices=state_list
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[validate_phone_number]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), ValidateGenreChoices()],
        choices=genre_list
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired(), Length(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(), Length(max=120), ValidateStateChoices()],
        choices=state_list
    )
    phone = StringField(
        'phone', validators=[DataRequired(), validate_phone_number]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), ValidateGenreChoices()],
        choices=genre_list
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=500)]
    )
    website = StringField(
        'website', validators=[URL(), Length(max=120)]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(), Length(max=500)]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
