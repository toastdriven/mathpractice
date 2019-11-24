# mathpractice

An app to help with practicing basic maths.


## Why?

To help my kids practice their basic math skills.

* Purposely a small app that doesn't deal with all the error states.
* Purposely doesn't have authentication.
* Simple in design & implementation.

Meant to be run siloed off in a home network, for 1-to-many people.


## Setup

```
$ git clone git@github.com:toastdriven/mathpractice.git
$ cd mathpractice
$ pipenv install

$ cd mathpractice
$ python

>>> import app
>>> app.db.create_tables([app.Problem])
```

## Running

```
$ pipenv shell
$ export APP_NAMES="daniel,john,jane"

# Optional, to enable debug mode.
# $ export APP_DEBUG=1

$ cd mathpractice
$ python app.py

# Alternatively, if you'll be changing the code, some hot-reloading...
# $ pipenv install gunicorn
# $ gunicorn -w 1 -t 0 app:app
```

Then hit up http://127.0.0.1/ in your browser.

## License

New BSD
