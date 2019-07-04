#!/bin/bash

export JWT_PRIVATE_KEY_FILE=/home/webapp/id_rsa
export JWT_PUBLIC_KEY_FILE=/home/webapp/id_rsa.pub
export JWT_ACCESS_TOKEN_EXPIRES=1210000
export FLASK_APP="/home/webapp/token-generator-ldap/app.py"
export FLASK_CONFIG_FILE="/home/webapp/production.cfg"
