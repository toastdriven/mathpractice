# mathpractice

An app to help with practicing basic maths.


## Why?

To help my kids practice their basic math skills.

* Purposely a small app that doesn't deal with all the error states.
* Purposely doesn't have authentication.
* Simple in design & implementation.

> **Note:** I'm running this app on a Raspberry Pi on my home network,
> siloed off from the rest of the internet. I'd **highly** recommend doing
> some similar (either just running locally or home network at most).
>
> **DO NOT EXPOSE THIS ON THE BROADER INTERNET!**


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

# Export the valid names to be displayed in the app.
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
