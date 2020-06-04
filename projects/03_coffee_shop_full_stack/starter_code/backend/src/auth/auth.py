import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import traceback


AUTH0_DOMAIN = 'p6l-richard.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://127.0.0.1/api'
# Authorize User:
#   POST https://p6l-richard.eu.auth0.com/authorize?response_type=token&client_id=<INSERT_CLIENT_ID>&redirect_uri=https://127.0.0.1:5000/login-results&audience=https://127.0.0.1/api
# Exchange auth code for token:
#   POST <see Postman for url>

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthError("Malformed - Authorization header", 403)
    token = auth_header.split(" ")[1]
    if not token:
        raise AuthError("Malformed - Authorization token", 403)
    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({"code": "invalid_token",
                                 "description": "can't read permission"}, 401)
    if permission not in payload['permissions']:
        raise AuthError({"code": "insufficient_permissions",
                                 "description": "required permission not found"}, 401)
    pass


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    # Get JWKS from auth0
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    # Store header from user token for later use
    unverified_header = jwt.get_unverified_header(token)

    # compare key id from user token to auth0's JWKS
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )
        except Exception as e:
            if str(e) == 'Signature has expired.':
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            elif str(e) == 'Invalid audience':
                raise AuthError({"code": "token_invalid",
                                 "description": "Wrong audience"}, 401)

            else:
                print('SOMETHING WENT WRONG', e)
                raise Exception('Failed')

        _request_ctx_stack.top.current_user = payload
        return payload

    raise AuthError({"code": "invalid_header",
                     "description": "Unable to find appropriate key"}, 401)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @ wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
                return f(payload, *args, **kwargs)
            except Exception as e:
                print(e)
                print(traceback.print_exc())
                return str(e)

        return wrapper
    return requires_auth_decorator
