import jwt
import datetime
from flask import request, jsonify
from functools import wraps

SECRET_KEY = 'tinyerp@key2024'

def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 900),#datetime.datetime.now() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow() ,#datetime.datetime.now(),
        'user': user_id,
        'role': 'superadmin'
    }
    gen_token = jwt.encode(payload, SECRET_KEY,'HS256')
    return gen_token

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY,'HS256')
        print("payload is -- ",payload)
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        print(request)
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            print('Token is missing!')
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            payload = decode_token(token)
            print("decoding token", payload['user'])
            #if isinstance(payload['user'], str):
                #return jsonify({'message': payload['user']}), 200
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated
