from os import path
import os
from flask import Flask


# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    ## Environment Settings ##
    # Enable debug mode.
    DEBUG = True
    SECRET_KEY = os.urandom(32)

    ## General Config ##
    FLASK_APP = basedir
    FLASK_ENV = "development"

    ## Database ##
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    # TODO IMPLEMENT DATABASE URL
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@localhost:5432/fyyur"
    # Connect to the database
    