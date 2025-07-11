# broker-api

[![Python](https://img.shields.io/static/v1?logo=python&label=python&message=3.13&color=blue)](#py313)
[![UV](https://img.shields.io/static/v1?logo=python-uv&label=uv&message=0.6.14&color=blue)](#uv0614)
[![Build Status](https://travis-ci.org/TheLazzziest/temp.svg?branch=master)](https://travis-ci.org/TheLazzziest/tempo)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)


A simple REST API for a broker. Check out the project's [documentation](http://TheLazzziest.github.io/broker-api/).

# Prerequisites

- [Docker](https://docs.docker.com/desktop/setup/install/linux/) + [Docker: Compose tool](https://docs.docker.com/compose/)
- [UV](https://github.com/astral-sh/uv)

# Quickstart

1. Configure thevirtual environment
```bash
uv venv && uv sync --group testing --group linting --group development
```
2. Start the dependencies:
```bash
docker compose up -d
```
3. Run migrations and collect static
```bash
uv run manage.py migrate && uv run manage.py collectstatic
```
5. Run tests
```bash
pytest
```
6. Create a superuser to login to the admin:
```bash
DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD uv run manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USER --email admin@local.host --skip-checks
```
7. Run API server
```bash
uv run manage.py runserver
```
8. You're ready to go tot `http://127.0.0.1:8000/docs/` ✔️
