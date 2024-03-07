#!/bin/sh

set -e

python3 manage.py migrate --noinput

gunicorn WiniPost.wsgi -b 0.0.0.0:8000
