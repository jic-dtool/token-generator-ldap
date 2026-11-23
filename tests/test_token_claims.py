"""Tokens carry the audience and issuer claims dserver requires."""

import os
import subprocess
import sys

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def env(tmp_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key = tmp_path / "jwt_key"
    private_key.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()))
    public_key = tmp_path / "jwt_key.pub"
    public_key.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo))
    config_file = tmp_path / "test.cfg"
    config_file.write_text('LDAP_HOST = "ldap://ldap.invalid"\n')

    env = {k: v for k, v in os.environ.items()
           if k not in ("JWT_AUDIENCE", "JWT_ISSUER")}
    env.update(FLASK_APP=os.path.join(REPO, "app.py"),
               FLASK_CONFIG_FILE=str(config_file),
               JWT_PRIVATE_KEY_FILE=str(private_key),
               JWT_PUBLIC_KEY_FILE=str(public_key))
    return env


def generate_token(env, **overrides):
    env = dict(env, **overrides)
    result = subprocess.run(
        [sys.executable, "-m", "flask", "generate-token", "alice"],
        env=env, capture_output=True, text=True, check=True)
    return result.stdout.strip().splitlines()[-1]


def claims(env, token):
    with open(env["JWT_PUBLIC_KEY_FILE"]) as fh:
        public_key = fh.read()
    return jwt.decode(token, public_key, algorithms=["RS256"],
                      options={"verify_aud": False, "verify_exp": False})


def test_default_audience_and_issuer_are_dserver(env):
    token = generate_token(env)
    with open(env["JWT_PUBLIC_KEY_FILE"]) as fh:
        public_key = fh.read()
    # Decodes with the checks dserver applies by default.
    decoded = jwt.decode(token, public_key, algorithms=["RS256"],
                         audience="dserver", issuer="dserver",
                         options={"verify_exp": False})
    assert decoded["sub"] == "alice"


def test_audience_and_issuer_from_environment(env):
    token = generate_token(env, JWT_AUDIENCE="my-dserver",
                           JWT_ISSUER="https://login.example.org")
    decoded = claims(env, token)
    assert decoded["aud"] == "my-dserver"
    assert decoded["iss"] == "https://login.example.org"


@pytest.mark.parametrize("value", ["", "  "])
def test_empty_values_leave_the_claims_out(env, value):
    decoded = claims(env, generate_token(env, JWT_AUDIENCE=value,
                                         JWT_ISSUER=value))
    assert "aud" not in decoded
    assert "iss" not in decoded
