JWT token generator web service authenticating against LDAP back end
====================================================================

Basic web app that allows a user to generate a JSON Web Token (JWT)
authenticating against a LDAP server.

End user usage::

    curl -H "Content-Type: application/json"  \
      -X POST -d '{"username": "olssont", "password": "secret" }'  \
      http://localhost:5000/token

Token consumer usage::

    curl http://localhost:5000/public_key

Installation::

    git clone REPO
    cd REPO
    pip3 install -r requirements

Configuration::

    export FLASK_APP=app.py
    export FLASK_CONFIG_FILE=production.cfg
    export JWT_PUBLIC_KEY_FILE=~/.ssh/id_rsa.pub
    export JWT_PRIVATE_KEY_FILE=~/.ssh/id_rsa

Optionally, the expiration time can changed from the default setting of 15
seconds, in the example below it is extended to two days::

    export JWT_ACCESS_TOKEN_EXPIRES=2880

Create a file named ``production.cfg`` with contents along the lines of the
below to allow the server to pass on the authentication of users to an external
LDAP server::

    LDAP_HOST="ldap://ldap.famousuni.ac.uk"
    LDAP_BASE_DN="ou=users,dc=famousuni,dc=ac,dc=uk"
    LDAP_USER_OBJECT_FILTER="(objectclass=person)"
    LDAP_SEARCH_FOR_GROUPS=False
    LDAP_USER_SEARCH_SCOPE="SUBTREE"
    LDAP_USER_LOGIN_ATTR="UID"
    LDAP_BIND_USER_DN=""
    LDAP_BIND_USER_PASSWORD=""


See `flask-ldap3-login <https://flask-ldap3-login.readthedocs.io>`_
documentation for more information on how to configure the connection to the
LDAP server.

Starting the server::

    flask run

Utility commands::

    flask generate-token <username>
    flask test-authentication <username>
