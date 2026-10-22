# Back-end-Development-Capstone

Django band website integrating Pictures and Songs services. Course project prepared from the IBM Skills Network starter template with AI assistance; review and understand the implementation before submission.

## Setup

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Validated locally with Python 3.14; container uses Python 3.12. No secrets are committed. The original Linux lab helper remains in `bin/setup.sh`; local validation used the virtual environment above.

## Run and test

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py test concert -v 2
```

Set `SONGS_URL` and `PICTURES_URL` to the service base URLs. Defaults: `http://127.0.0.1:5001` and `http://127.0.0.1:5002`. Eight tests cover authentication, signup, attendance ownership and updates, missing concerts, service integration/failure, and admin access.

The site has Home, Songs (lyrics modal), Photos, Login, Signup, Concerts and Django Admin. Concert attendance requires login and a valid POST/CSRF token. Administrative concert CRUD uses Django Admin.

## Deployment

Build with `docker build -t djangoserver .`. Set a fresh `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `SONGS_URL` and `PICTURES_URL`. Use `/data` as a persistent volume for SQLite in this single-replica lab. The entrypoint applies committed migrations, and never creates an admin with a hard-coded password. Run `createsuperuser` interactively after deployment.

`deployment.yml` is a template: replace the image/host/service placeholders and create the `django-config` secret before applying. Cloud deployment was verified on 22 October 2026: Django runs in Kubernetes, Pictures in Code Engine, and Songs with MongoDB in OpenShift. Home, Songs and Photos were checked in Chrome. The lab uses `emptyDir`, so replacing the Django pod resets SQLite data; use a persistent volume for durable data. The OpenShift route was unreachable from this lab, so Songs is connected through the Skills Network port-forward proxy. Both forwards require active lab sessions. Upstream requests allow a 5-second connection timeout and 25-second read timeout for cold starts. Set `GUNICORN_CMD_ARGS=--no-control-socket` in this lab environment.

## Container

The Dockerfile runs Gunicorn as an unprivileged user. Preserve the original IBM licensing and attribution.
