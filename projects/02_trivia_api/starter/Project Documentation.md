# Udacitrivia
This project is a trivia app that helps Udacity employees more easily quiz
each other with fun and exicting trivia. The app can store questions with the
necessary information to create complete quizes. Questions can also be searched by prividing a category or by matching text in the question.

The project follows [Pep8 style guidelines](https://www.python.org/dev/peps/pep-0008/) for formatting code.

## Getting Started
### PosgtreSQL Database
A local installation of PostgreSQL is needed to run the application. Installation instructions
can be found on the [Postgres site](https://www.postgresqltutorial.com/install-postgresql/).
Alternatively, Digitalocean offers a great [tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04) for installing PostgreSQL on
Ubunut, CentOS, and Debian.

By default, the app connects to a database at `localhost` using port `5432`. The default 
username is `trivia_app`. The database user is required to have a password if the app is 
being run on a Linux distro such as Ubuntu.

#### Database Setup
Follow these steps to set up the database:
  - Activate the **postgres** user with the command:
    ```
    sudo -i -u postgres
    ```
  - Create a database named `trivia` with the command:
    ```
    createdb trivia
    ```
  - Create a user named `trivia_app` with the command:
    ```
    createuser --interactive
    ```
    - The command will ask a series of questions that can all be answered with a no
    - **NOTE**: Answering no to all the questions is fine since the user is only needed
      to give the app access to the database and does not need to manage the database or tables
  - Run the psql interpretor with the command:
    ```
    psql
    ```
  - To change the database user password, run the psql command:
    ```
    \password trivia_app
    ```
    - This password is needed to connect the app to the local database
    - **NOTE**: This step is necessary to connect to the database using password based 
      authentication on Linux machines instead of peer based authentication because of default
      configurations the psycopg2 library uses when connecting to postgres on some Linux distros
  - Exit out of psql interpretor using the psql command `\q` 
  - Traverse to the `backend/` directory in the project
  - From the `backend/` directory, run the command:
    ```
    psql trivia < trivia.sql
    ```
    - This will populate the database with data and grant
      the user `trivia_app` ownership of the trivia database tables
  - Run the `exit` command to exit out of the postgres user shell login

#### Verify Setup Worked
Connect to the database with the command:
```
psql trivia --username trivia_app --host localhost
```
  - Providing the `--host` or `-h` flag will ask for the database user password instead of
    attempting peer authentication using the system user

Display the `trivia` database tables with the commannd:
```
\dt
```

Display the `questions` schema with the command:
```
\d questions
```

Display the `questions` rows using the command:
```
SELECT * FROM questions;
```

### Flask Web API
The web API uses Python and Flask. For this project, Anaconda is being used to manage 
Python packages and the virtual environments. Installation instructions can be found on the
[Conda documentation](https://docs.conda.io/projects/continuumio-conda/en/latest/user-guide/install/index.html#) 
page. For a lean installation of just the conda command, there are instructions for installing
Miniconda as well. 

#### Virtual Environment
Creating a virtual environment is recommended to keep the project packages separate from any 
Python packages that may be installed on the host computer. The conda command provided by
Anaconda or Miniconda, will be used to manage the virtual environment.


Traverese to the `backend/` directory in the project folder and run the command:
```
conda env create --file environment.yml
```

To change the environment name used, use the `--name` flag when running the command:
```
conda env create --file environment.yml --name alternate_name
```

To export the current environment, run the command:
```
conda env export --file environment.yml
```

The last line in the `environment.yml` file can be removed, since it contains the
path where the environment is installed on the host computer and does not affect the
creation of the environment on other computers.

#### Additional Dependencies
On a Linux system, it may be neccessary to install additional dependencies
to allow the psycopg2 Python library to communicate with PostgreSQL. The dependencies are
`python-psycopg2` and `libpq-dev` and can be installed on Ubuntu using the command:
```
apt install python-psycopg2 libpq-dev
```

#### Running the Web API
Activate the virtual environment with the command:
```bash
conda activate trivia_api 
```

Traverse to the `backend/` directory in the project folder and create these Flask app environment variables:
```
export FLASK_APP=flaskr
export FLASK_ENV=development
```
  - FLASK_APP tells Flask the name of the file or module the app is located in
  - When FLASK_ENV is set to developmet, Flask restarts the app whenever a file is updated

From the `backend/` directory, run the command
```
flask run
```

There will be a message similar to:
```
 * Serving Flask app "flaskr" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 233-700-124
```
The web API will be available at the url in the output. In this case at
`http://127.0.0.1:5000/`.

#### Running Web API Tests
Web API tests are located in the `backend` directory in the `test_flaskr.py` file. 

In order to run the tests within the `test_flasker.py` file, the system user requires
authorization to create and delete databases. The postgres database user must have
the same name as the system user.

Create a database user with the command:
```
sudo -u postgres createuser --interactive
```
  - **NOTE**: Answer yes to the question: `Shall the new role be a superuser? (y/n)`

Run the tests with the command:
```
python test_flaskr.py
```

### React Web App
The web app is written using JavaScript and the React library. It is recommended to [install
nvm](https://github.com/nvm-sh/nvm#installing-and-updating) to manage Node.js versions.

With node installed, enter the `frontend/` directory in the project folder and run the command:
```
npm install
```
  
Run the app with the command:
```
npm start
```
