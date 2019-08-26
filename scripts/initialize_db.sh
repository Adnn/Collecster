#!/bin/bash

python3 manage.py migrate &&             \
# Why is that fixture not an "initial_xxx" like the others? (i.e. applied by the initial_data fixture)
python3 manage.py loaddata groups
