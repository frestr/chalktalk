# chalktalk

[![Coverage Status](https://coveralls.io/repos/github/frestr/chalktalk/badge.svg?branch=dev)](https://coveralls.io/github/frestr/chalktalk?branch=dev)

Project for the course "Software Development"

To set up project:

```
pip install virtualenv
git clone https://github.com/frestr/chalktalk.git
virtualenv chalktalk
source chalktalk/bin/activate
cd chalktalk
export FLASK_APP=runserver.py
flask run
```

For virtualenv on windows, see here: https://virtualenv.pypa.io/en/stable/userguide/#usage

To run the tests, do:
```
python -m unittest discover
```

in the project root directory
