#!/usr/bin/env bash
# exit on error
set -o errexit
pip install --upgrade pip

poetry install
poetry self update 1.2.2
pip install --force-reinstall -U setuptools
python manage.py collectstatic --no-input
python manage.py migrate