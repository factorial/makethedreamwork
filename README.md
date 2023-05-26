# makethedreamwork

This is the codebase for makethedreamwork.com.
It's a proof of concept tool that illustrates a few concepts, some even intentionally:

* Using AI to build & empower teams of humans to accomplish the big things.
* AI group chat.
* An unholy marriage of Django and FastAPI (Django models & HTML views + FastAPI Eventstream responses)
* Making the most of developer time by writing the sloppiest, hackiest thing imaginable, directly on a single weak production server.

## Slow start

This code is sloppily written and hastily conceived. Set up is not streamlined.

If you want to get up and running, here's a rough outline:

* New Ubuntu host
* Put this codebase in `/home/ubuntu/mysite/`
* mkdir `team/static/i/`
* Create `team/secrets.py`:
```
SECRET_KEY="make something up"
OPENAI_API_KEY="get it from your openai account"
```
* Install nginx
* Include `site_nginx.conf` in your nginx configs
* Do the venv stuff
* `pip install -r requirements.txt`
* Use the uwsgi and wsgi files in `team` to Set up a uWSGI service running the Django app in `team`, which manages port 80 HTTP requests (pages)
* Use the `team/uvicorn.service` file to set up a Uvicorn service running the FastAPI app in `stream`, which manages port 5000 for Eventstream requests (chats)
* `python manage.py migrate`

If you're reading this, sorry. This wasn't really intended to be shared.
