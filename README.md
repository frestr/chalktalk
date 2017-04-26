# chalktalk

[![Build Status](https://travis-ci.org/frestr/chalktalk.svg?branch=master)](https://travis-ci.org/frestr/chalktalk)
[![Coverage Status](https://coveralls.io/repos/github/frestr/chalktalk/badge.svg?branch=dev)](https://coveralls.io/github/frestr/chalktalk?branch=dev)

Project for the course "Software Development"

## Project Structure
This is the main project structure:
```
chalktalk
├── chalktalk        # Python files
│   ├── static       # Static files (css, js, images)
│   │   ├── css
│   │   ├── fonts
│   │   ├── images
│   │   └── js
│   └── templates    # Jinja2 HTML templates
├── runserver.py     # Script file used to launch application
├── setup_test_db.py # Script to set up a database with dummy values
└── tests            # Unit & integration tests
```

## Configuration

Do the following steps to set up a development instance of the program.

### 0. Program requirements

Make sure Python 3 and SQLite3 are installed.

### 1. Set up virtualenv

```
pip3 install virtualenv
git clone https://github.com/frestr/chalktalk.git
virtualenv chalktalk
source chalktalk/bin/activate
cd chalktalk
```

### 2. Install the dependencies

```
pip3 install -r requirements.txt
```

### 3. Set configuration files

Copy the settings example file:
```
cp chalktalk/settings.py.example chalktalk/settings.py
```
and change the content of settings.py to contain the file location of the
database (doesn't have to exist yet).

For example, if the database file is located in the project root directory, the
file path can be 
```
DATABASE_URL = 'sqlite:///database.db'
```

Copy the secret settings example file:
```
cp chalktalk/secret_settings.py.example chalktalk/secret_settings.py
```
and change the cookie signing key and the Dataporten OAUTH credentials. If
Dataporten is not to be used, the values should be kept unchanged.

### 4. Create the database

If you want to generate a test database with some dummy values, do
```
./setup_test_db.py
cp dummy.db database.db
```

If not, just make sure the database file exists:
```
touch database.db
```

### 5. Start the dev server

```
export FLASK_APP=runserver.py
flask run
```

## Tests
To run the tests, do:
```
python -m unittest discover
```
in the project root directory
