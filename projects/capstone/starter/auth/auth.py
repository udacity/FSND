import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen



AUTH0_DOMAIN = 'dev-md-8ge9f.us.auth0.com'
ALGORITHMS = ['RS256']
API_MOVIE_PRODUCER = 'movie_producer'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
oauth = None

current_token = None

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def setup_auth(app):
    app.logger.info("CALLED AND SAVED")
    #oauth = OAuth(app)
    
# Auth Header

#def login_authentication():
#    login_link = f'https://{AUTH0_DOMAIN}/authorize?audience={AUDIENCE}&response_type=token&client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}'

def set_current_token(token):
    current_token = None


def get_token_auth_header():
    if current_token is not None or False:
        token = current_token
    else:

        if 'Authorization' not in request.headers:
            abort(401)
        auth_header = request.headers['Authorization']
        header_parts = auth_header.split(' ')

        if len(header_parts) != 2:
            abort(401)
        elif header_parts[0].lower() != 'bearer':
            abort(401)

        token = header_parts[1]

    return token

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)


    if permission not in payload['permissions']:
        abort(403)

    return True

def verify_decode_jwt(token, permission):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    
    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_MOVIE_PRODUCER,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token, permission)
            except:
                abort(403)
            #app.logger.info('payload: ' + payload)
            result = check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
