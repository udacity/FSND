import os
from typing import Any

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

psql_user: str = os.getenv("PSQL_USER", "postgres")
db_port: Any = os.getenv("PSQL_PORT", 5432)
db_name: str = os.getenv("DB_NAME", "fyyur")
app_settings: str = f"{basedir}/config.py"
os.environ["APP_SETTINGS"] = app_settings
os.environ["PORT"] = str(9001)

# Enable debug mode.
# TODO IMPLEMENT DATABASE URL


class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{psql_user}@localhost:{db_port}/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

# Connect to the database
