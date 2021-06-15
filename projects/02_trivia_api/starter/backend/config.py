# Flask configuration

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = 'GDtfDCFYjD'
DATABASE_URI = "postgres://{}/{}".format('postgres:Ran!dom101@127.0.0.1:5432', 'trivia')
APP_VERSION = 'v1.0'