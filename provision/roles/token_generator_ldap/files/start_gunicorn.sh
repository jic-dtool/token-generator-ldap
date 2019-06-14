#!/bin/bash

source load_env.sh
source /home/webapp/venv/bin/activate
cd token-generator-ldap
exec gunicorn -D -b :5000 --access-logfile /home/webapp/logs/access.log --error-logfile /home/webapp/logs/error.log --pid /home/webapp/gunicorn.pid "app:app"
cd ..
