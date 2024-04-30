#!/bin/bash
python manage.py reset_db
ls -R */migrations/000*.py | xargs rm 
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixture.json
ls -R */migrations/000*.py | xargs rm 
