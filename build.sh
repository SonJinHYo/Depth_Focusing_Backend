#!/usr/bin/env bash
# exit on error
set -o errexit
pip install --upgrade pip
pip install gdown

gdown https://drive.google.com/uc?id=1lvyZZbC9NLcS8a__YPcUP7rDiIpbRpoF
mv AdaBins_nyu.pt ./medias/depth_model/pretrained/AdaBins_nyu.pt

git lfs install
poetry install
pip install --force-reinstall -U setuptools
python manage.py collectstatic --no-input
python manage.py migrate