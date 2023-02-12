#!/usr/bin/env bash
# exit on error
set -o errexit
pip install --upgrade pip

poetry install
poetry lock
pip install --force-reinstall -U setuptools
python manage.py collectstatic --no-input
python manage.py migrate