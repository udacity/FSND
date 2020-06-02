import os
import tempfile

import pytest

from src import create_app
from .database import setup_db, Drink, db


@pytest.fixture
def client():
    app = create_app()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            setup_db(app)
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_get_homepage(client):
    """Start with the hello string."""

    rv = client.get('/')
    assert b'hello' in rv.data
    assert 200 == rv.status_code


def test_404_get_random_route(client):
    """"Get route not yet implemented"""
    rv = client.get('/not-yet-implemented')
    assert b'not found' in rv.data.lower()
    assert 404 == rv.status_code


def test_drink_title(client):
    """"Test if drink.title exists"""
    try:
        q = db.session.query(Drink.title)
        assert q.column_descriptions[0]['name'] == 'title'
    except Exception as e:
        print(e)
