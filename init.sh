#!/usr/bin/env bash

docker exec -it mailissue python manage.py makemigrations app1
docker exec -it mailissue python manage.py migrate
docker exec -it mailissue python manage.py createsuperuser