#!/bin/bash

python -m pip install --user --upgrade pip

python -m pip install --user virtualenv

python -m venv env

source env/bin/activate

python -m pip install -r requirements.txt

pip install git+https://github.com/openai/CLIP.git

python manage.py migrate

python manage.py compilemessages

python manage.py runserver