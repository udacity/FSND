import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# IMPLEMENT DATABASE URL
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_USER = os.getenv('DB_USER', 'jserra02')
DB_NAME = os.getenv('DB_NAME', 'fyyur')
DB_PATH = 'postgresql://{}@{}/{}'.format(DB_USER, DB_HOST, DB_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS  = False