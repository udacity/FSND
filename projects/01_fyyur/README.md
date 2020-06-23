Fyyur
-----

### Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

Your job is to build out the data models to power the API endpoints for the Fyyur site by connecting to a PostgreSQL database for storing, querying, and creating information about artists and venues on Fyyur.

### Overview

This app is nearly complete. It is only missing one thing… real data! While the views and controllers are defined in this application, it is missing models and model interactions to be able to store retrieve, and update data from a database. By the end of this project, you should have a fully functioning site that is at least capable of doing the following, if not more, using a PostgreSQL database:

* creating new venues, artists, and creating new shows.
* searching for venues and artists.
* learning more about a specific artist or venue.

We want Fyyur to be the next new platform that artists and musical venues can use to find each other, and discover new music shows. Let's make that happen!

### Tech Stack

Our tech stack will include:

* **SQLAlchemy ORM** to be our ORM library of choice
* **PostgreSQL** as our database of choice
* **Python3** and **Flask** as our server language and server framework
* **Flask-Migrate** for creating and running schema migrations
* **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend

### Main Files: Project Structure

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependences
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

### Development Setup

1. Install Python 3.7 or higher
2. [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.
3. Install postgresql on the machine
4. install virtualenv on your computer


  ```
  Linux:
  $ cd ~
  $ sudo pip3 install Flask, virtualenv

  Windows:
  $ cd %HOME%
  $ pip install Flask, virtualenv
  ```

To start and run the local development server:

Initialize and activate a virtualenv:
  ```
  Linux: 
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ virtualenv --no-site-packages env
  $ source env/bin/activate
  
  Windows:
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ python -m virtualenv env
  $ .\env\Scripts\activate.bat
  ```
Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```
create the fyyur db:
  ```
  $ createdb fyyur
  ```
create .secrets file in project root with connection setup info:
```
{
  "username": "username",
  "password": "password"
}
```

run Migration script:
```
    python -m flask db migrate
```

Run the development server:
  ```
  $ export FLASK_APP=myapp
  $ export FLASK_ENV=development # enables debug mode
  $ python3 app.py
  ```

Navigate to Home page [http://localhost:5000](http://localhost:5000)
