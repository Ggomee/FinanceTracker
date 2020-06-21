# finance-tracker20

## Quickstart

Make a Python 3 virtual environment, activate it, and install the dependencies.
For example, on Linux,

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run dev server using,

```sh
python -m flaskblog
```

Or

```sh
gunicorn flaskblog:app
```


## Deploy

Make sure you have a Heroku account, and make a app
After cloning this repo,

```sh
heroku login
heroku git:remote -a your-app-name
git push heroku master
```

And visit https://your-app-name.herokuapp.com/

If you found any error, run `heroku logs --tail` to see the log messages.
