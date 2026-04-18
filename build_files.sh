#!/bin/bash

# Force install requirements into the Vercel environment
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt --break-system-packages

# Run collectstatic
python3 manage.py collectstatic --noinput --clear
