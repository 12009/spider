from flask import request, session
from flask_restful import reqparse
from utils.time import formatTimestamp
from common import db

def verify_token(func):
    def _wrapper(*args, **kwargs):
        token = request.headers['token']
        appObj = db.fetchone("select * from app where token=:token", {'token':token})
        if not appObj:
            return {'status':'failed', 'msg':'token error', 'token':token}, 200
        session['app'] = appObj
        return func(*args, **kwargs)
    return _wrapper

