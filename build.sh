#!/usr/bin/env bash
# exit on error
set -o errexit
pip install --upgrade pip

poetry self update
poetry install
pip install --force-reinstall -U setuptools
python manage.py collectstatic --no-input
python manage.py migrate