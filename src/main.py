#!/usr/bin/env python3

from WellKnownHandler import WellKnownHandler
from WellKnownHandler import TYPE_UMA_V2, KEY_UMA_V2_RESOURCE_REGISTRATION_ENDPOINT, KEY_UMA_V2_PERMISSION_ENDPOINT, KEY_UMA_V2_INTROSPECTION_ENDPOINT

from flask import Flask, request, Response
from werkzeug.datastructures import Headers
from random import choice
from string import ascii_lowercase
from requests import get, post, put, delete
import json

from config import get_config
from eoepca_scim import EOEPCA_Scim, ENDPOINT_AUTH_CLIENT_POST
from handlers.oidc_handler import OIDCHandler
from handlers.uma_handler import UMA_Handler, resource
from handlers.uma_handler import rpt as class_rpt
from handlers.mongo_handler import Mongo_Handler
from handlers.policy_handler import policy_handler
import blueprints.resources as resources
import blueprints.proxy as proxy
import os
import sys
import traceback

from jwkest.jws import JWS
from jwkest.jwk import RSAKey, import_rsa_key_from_file, load_jwks_from_url, import_rsa_key
from jwkest.jwk import load_jwks
from Crypto.PublicKey import RSA
import logging
logging.getLogger().setLevel(logging.INFO)

### INITIAL SETUP
g_config, g_wkh = get_config("config/config.json")

oidc_client = OIDCHandler(g_wkh,
                            client_id = g_config["client_id"],
                            client_secret = g_config["client_secret"],
                            redirect_uri = "",
                            scopes = ['openid', 'uma_protection', 'permission'],
                            verify_ssl = g_config["check_ssl_certs"])

uma_handler = UMA_Handler(g_wkh, oidc_client, g_config["check_ssl_certs"])
uma_handler.status()

#PDP Policy Handler
pdp_policy_handler = policy_handler(pdp_url=g_config["pdp_url"], pdp_port=g_config["pdp_port"], pdp_policy_endpoint=g_config["pdp_policy_endpoint"])

def generateRSAKeyPair():
    _rsakey = RSA.generate(2048)
    private_key = _rsakey.exportKey()
    public_key = _rsakey.publickey().exportKey()

    file_out = open("config/private.pem", "wb+")
    file_out.write(private_key)
    file_out.close()

    return private_key

private_key = generateRSAKeyPair()

app = Flask(__name__)
app.secret_key = ''.join(choice(ascii_lowercase) for i in range(30)) # Random key

# Register api blueprints (module endpoints)
app.register_blueprint(resources.construct_blueprint(oidc_client, uma_handler, pdp_policy_handler, g_config))
app.register_blueprint(proxy.construct_blueprint(oidc_client, uma_handler, g_config, private_key))

# Start reverse proxy for x endpoint
app.run(
    debug=g_config["debug_mode"],
    threaded=g_config["use_threads"],
    port=int(g_config["service_port"]),
    host=g_config["service_host"]
)
