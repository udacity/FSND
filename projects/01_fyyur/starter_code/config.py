import os
import json
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
password_path = basedir + '/.secrets'
print('password_path: {}'.format(password_path))
data = dict()
if os.path.isfile(password_path):
    with open(password_path, 'r') as json_file:
        data = json.load(json_file)
        print(f'data: {data}')
else:
    print('No .secrets file detected.')

username = data.get('username', 'postgres')
password = data.get('password')
host = data.get('host', 'localhost')
port = data.get('port', '5432')
database_name = data.get('database_name', 'fyyur')

if password:
    userpass = '{}:{}'.format(username, password)
else:
    userpass = '{}'.format(username)

SQLALCHEMY_DATABASE_URI = f'postgresql://{userpass}@{host}:{port}/{database_name}'
print(f'SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}')
SQLALCHEMY_TRACK_MODIFICATIONS = False
