import os

import click

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_ldap3_login import LDAP3LoginManager


def get_file_content(key, default=""):
    file_path = os.environ.get(key, "")
    if os.path.isfile(file_path):
        content = open(file_path).read()
    else:
        content = ""
    return content


class Config(object):

    JWT_ALGORITHM = "RS256"
    JWT_PRIVATE_KEY = get_file_content("JWT_PRIVATE_KEY_FILE")
    JWT_PUBLIC_KEY = get_file_content("JWT_PUBLIC_KEY_FILE")
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 15)
    )


app = Flask(__name__)
CORS(app)

app.config.from_envvar("FLASK_CONFIG_FILE")
app.config.from_object(Config)

# Initialise the JSON Web Token Manager.
jwt = JWTManager()
jwt.init_app(app)

# Initialise the ldap manager using the settings read into the flask app.
ldap_manager = LDAP3LoginManager(app)


@app.route("/")
def index():
    return "JWT token generation service authenticating against LDAP back end"


@app.route("/public_key")
def public_key():
    return app.config["JWT_PUBLIC_KEY"]


@app.route("/token", methods=["POST"])
def token():
    data = request.get_json()

    # Parse username and password.
    for required_key in ["username", "password"]:
        if required_key not in data:
            abort(400)
    username = data["username"]
    password = data["password"]

    # Authenticate.
    ldap_response = ldap_manager.authenticate(username, password)

    response = {}
    response["status"] = ldap_response.status.name
    if ldap_response.status.name == "success":
        token = create_access_token(identity=username)
        response["token"] = token

    return jsonify(response)


#############################################################################
# Command line helper utilities.
#############################################################################

@app.cli.command()
@click.argument('username')
@click.option("--last-forever", is_flag=True)
def generate_token(username, last_forever):
    """Generate token."""
    if last_forever:
        token = create_access_token(identity=username, expires_delta=False)
    else:
        token = create_access_token(identity=username)
    print(token)


@app.cli.command()
@click.argument('username')
@click.option('--password', prompt=True, hide_input=True)
def test_authentication(username, password):
    """Test authentication."""
    ldap_response = ldap_manager.authenticate(username, password)
    print(ldap_response.status)
