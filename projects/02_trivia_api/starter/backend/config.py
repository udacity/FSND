# Flask configuration

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = 'GDtfDCFYjD'
DATABASE_URI = "postgresql://{}/{}".format('postgres:Ran!dom101@localhost:5432', 'trivia')
APP_VERSION = 'v1.0'