import re
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import InputRequired, AnyOf, URL, Optional, ValidationError


state_choices = [
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


def filter_empty_strings(value):
    if type(value) == str and value.strip() == '':
        return None
    else:
        return value


class PhoneNumber(object):
    def __init__(self, message=None):
        if not message:
            message = u'phone number must have the format ###-###-####'
        self.message = message

    def __call__(self, form, field):
        pattern = r'^\d{3}-\d{3}-\d{4}$'
        if field.data and not re.match(pattern, field.data):
            raise ValidationError(self.message)


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[InputRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[InputRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[InputRequired()],
        default=datetime.today()
    )


class VenueForm(FlaskForm):
    name = StringField(
        'name',
        validators=[InputRequired()]
    )
    city = StringField(
        'city',
        validators=[InputRequired()]
    )
    state = SelectField(
        'state',
        validators=[InputRequired()],
        choices=state_choices
    )
    address = StringField(
        'address',
        validators=[InputRequired()]
    )
    phone = StringField(
        'phone',
        validators=[Optional(), PhoneNumber()],
        filters=[filter_empty_strings]
    )
    genres = SelectMultipleField(
        'genres',
        coerce=int
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL()],
        filters=[filter_empty_strings]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL()],
        filters=[filter_empty_strings]
    )
    website = StringField(
        'website',
        validators=[Optional(), URL()],
        filters=[filter_empty_strings]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description',
        filters=[filter_empty_strings]
    )


class ArtistForm(FlaskForm):
    name = StringField(
        'name',
        validators=[InputRequired()]
    )
    city = StringField(
        'city',
        validators=[InputRequired()]
    )
    state = SelectField(
        'state',
        validators=[InputRequired()],
        choices=state_choices
    )
    phone = StringField(
        'phone',
        validators=[Optional(), PhoneNumber()],
        filters=[filter_empty_strings]
    )
    genres = SelectMultipleField(
        'genres',
        coerce=int
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL()],
        filters=[filter_empty_strings]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL()],
        filters=[filter_empty_strings]
    )
    website = StringField(
        'website',
        validators=[Optional(), URL()],
        filters=[filter_empty_strings]
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description',
        filters=[filter_empty_strings]
    )
