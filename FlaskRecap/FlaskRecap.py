from flask import Flask, request, jsonify, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import json

app = Flask(__name__)

greetings = {
            'en': 'hello', 
            'es': 'Hola', 
            'ar': 'مرحبا',
            'ru': 'Привет',
            'fi': 'Hei',
            'he': 'שלום',
            'ja': 'こんにちは'
            }
AUTH0_DOMAIN = 'fsnd-saylesc.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://fsnd-auth'
AUTHORIZATION = 'Authorization'
BEARER = 'bearer'

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
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
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication header'
            }, 401)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the ppropriate authentication header'
    }, 401)

def get_auth_token_header():
    if AUTHORIZATION not in request.headers:
        # Not authorized
        abort(401)

    auth_header = request.headers['Authorization']
    header_token = auth_header.split(' ')

    if len(header_token) != 2:
        abort(401)
    elif header_token[0].lower() != BEARER:
        abort(401)

    return header_token[1]

def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        jwt = get_auth_token_header()
        try:
            payload = verify_decode_jwt(jwt)
        except:
            abort(401)
        
        return f(payload, *args, **kwargs)
    return wrapper

@app.route('/headers')
@requires_auth
def headers(jwt):
    print(jwt)
    return 'not implemented...yet'

@app.route('/greeting', methods=['GET'])
def greeting_all():
    return jsonify({'greetings': greetings})

@app.route('/greeting/<lang>', methods=['GET'])
def greeting_one(lang):
    print(lang)
    if(lang not in greetings):
        abort(404)
    return jsonify({'greeting': greetings[lang
    ]})

@app.route('/greeting', methods=['POST'])
def greeting_add():
    info = request.get_json()
    if('lang' not in info or 'greeting' not in info):
        abort(422)
    greetings[info['lang']] = info['greeting']
    return jsonify({'greetings':greetings})
