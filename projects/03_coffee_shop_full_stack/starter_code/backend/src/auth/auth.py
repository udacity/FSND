import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

# https://dev-ast.us.auth0.com/authorize?&audience=https://coffe_shope/drinks&response_type=token&client_id=2nHWumFKu6k24ClMdld9AO61LSwv4ZE0&redirect_uri=http://localhost:8100/tabs/user-page
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlR4dkJVbEZaTHZCaHRZMm1RM243dyJ9.eyJpc3MiOiJodHRwczovL2Rldi1hc3QudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmNjY1MDZlNDQxOWFhMDA3MTdmNjFmYiIsImF1ZCI6Imh0dHBzOi8vY29mZmVfc2hvcGUvZHJpbmtzIiwiaWF0IjoxNjAxMDA2MDM4LCJleHAiOjE2MDEwMTMyMzgsImF6cCI6IjJuSFd1bUZLdTZrMjRDbE1kbGQ5QU82MUxTd3Y0WkUwIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWxzIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.NQ4uD8kTuRNJLTBG_WzXTkgRABNSvcYngZfn8FMUBkBIlu4XoIDrLD5-5VOUgPeJKT-rlA8xQFLRYVXi6Rj0slK9eVFW9cx-ZotM_7M6xO-jqP8lAShWroG7o5tE9kMKJlnGZv2qIfcB7ws3Eyr7QloMNaTCtJKrwHsgJN0TslZuWAMAD0tserrfxiQnYkkWFyI8sPyHpvu46dMvvUdMI_z9Nj0fzX9DSQDwSXJEMGHtDqN0PL_UWqP7MRjZduOAl-N3DWkmP9frDp28WgxLc72WhN5HnELBeNpI1zypBIA5PfQrxxt3kdAu8ycFPJSktRAF-wnMgIYLFfZHlMtbrg
AUTH0_DOMAIN = 'dev-ast.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coffe_shope/drinks'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    print(auth)
    if not auth:
        raise AuthError({
            'code': '401',
            'description': 'Authorization header is expected'
        }, 401)

    part = auth.split()
    if part[0].lower() != 'bearer':
        raise AuthError({
            'code': '401',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(part) == 1:
        raise AuthError({
            'code': '401',
            'description': 'Token not found'
        }, 401)

    elif len(part) > 2:
        raise AuthError({
            'code': '401',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    
    token = part[1]
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
    if "permission" in payload:
        return True
    raise Exception('Not Implemented')

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
    jsonurl = urlopen('https://dev-ast.us.auth0.com/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
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
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(*args, **kwargs)
        return wrapper
    return requires_auth_decorator