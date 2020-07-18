import sys
import os
import json
from jose import jwt
from urllib.request import urlopen


# Configuration
# UPDATE THIS TO REFLECT YOUR AUTH0 ACCOUNT
AUTH0_DOMAIN = 'flis.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'


def get_secrets():
    basedir = os.path.abspath(os.path.dirname(__file__))
    secrets_path = basedir + '/.secrets'
    print('secrets_path: {}'.format(secrets_path))

    data = dict()
    if os.path.isfile(secrets_path):
        with open(secrets_path, 'r') as json_file:
            data = json.load(json_file)
            print(f'data: {data}')
    else:
        print('No .secrets file detected.')
        pass

    token = data.get('token')
    print(f'token: {token}')
    return token


'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    print(f'jwks:\n{json.dumps(jwks, indent=2)}')

    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)
    print(f'unverified_header:\n{json.dumps(unverified_header, indent=2)}')

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
                audience=API_AUDIENCE,
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


if __name__ == '__main__':
    token = get_secrets()
    payload = verify_decode_jwt(token)
    print(f'payload:\n{json.dumps(payload, indent=2)}')
