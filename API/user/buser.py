#
#
#   User.py
#
#


from datetime import datetime
from flask import current_app
from pymongo import Connection
import hashlib
import redis
import json


conn = Connection(current_app.config.get('MONGO_URL'))
db = conn['blibb']
objects = db['users']


class User(object):

    @classmethod
    def get_redis(self):
        return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    @classmethod
    def create(cls, name, email, password, code):
        if cls.is_available(name, email):
            now = datetime.utcnow()
            salt = hashlib.sha1(email + str(datetime.utcnow())).hexdigest()
            pub_salt = hashlib.sha1(email + str(datetime.utcnow())).hexdigest()
            reset_password = hashlib.sha1(email + str(datetime.utcnow())).hexdigest()
            password = hashlib.sha1(password + salt).hexdigest()
            user_id = objects.insert(
                    {"n": name, "e": email, "p": password,
                    "s": salt, "ps": pub_salt, "c": now,
                    "a": True, 'l': now, 'rc': code, 'rp': reset_password})
            return str(user_id)
        else:
            return None

    @classmethod
    def authenticate(self, user, password):
        stUser = objects.find_one({'$or': [{'e': user.strip()}, {'n':user.strip()}]})
        if stUser is not None:
            shPwd = hashlib.sha1(password + stUser['s'])
            if stUser['p'] == shPwd.hexdigest():
                stUser['la'] = datetime.utcnow()
                objects.save(stUser)
                user = self.flat_object(stUser)
                key = self.setKey(user)
                user['key'] = key
                return user
        return False

    @classmethod
    def get_user(cls, key):
        r = cls.get_redis()
        return r.get(key)

    @classmethod
    def logout(self, key):
        r = self.get_redis()
        return r.delete(key)

    @classmethod
    def setKey(self, user):
        r = self.get_redis()
        userkey = hashlib.sha1(user['username'] + user['id'] + str(datetime.utcnow())).hexdigest()
        r.set(userkey, json.dumps(user))
        expire = current_app.config.get('EXPIRE')
        r.expire(userkey, expire)

        return userkey

    @classmethod
    def get_object(self, filter, fields={}):
        return objects.find_one(filter, fields)

    @classmethod
    def get_by_name(self, username):
        doc = self.get_object({'n': username}, {'p': 0, 's': 0})
        return self.flat_object(doc)

    @classmethod
    def add_picture(self, filter, image):
        objects.update(filter, {"$set": {'u': image}}, True)

    @classmethod
    def is_admin(self, user):
        doc = self.get_by_name(user)
        if doc is not None:
            role = doc.get('role', '')
            if role == 'admin':
                return True
        return False

    @classmethod
    def flat_object(self, doc):
        buf = dict()
        if doc:
            buf['id'] = str(doc['_id'])
            if 'n' in doc:
                buf['username'] = doc['n']
            if 'e' in doc:
                buf['email'] = doc['e']
            if 'r' in doc:
                buf['role'] = doc['r']
            # if 'i' in doc:
            #         img = doc['i']
            #         buf['image'] = str(img['id'])
            if 'a' in doc:
                buf['status'] = doc['a']
            if 'u' in doc:
                buf['image_url'] = doc['u']
            else:
                buf['image_url'] = current_app.config.get('STATIC_URL') + 'default.png'

        return buf

    @classmethod
    def is_available(cls, username, email):
        doc = cls.get_object({'$or': [{'n': username}, {'e': email}]})
        if doc is None:
            return True
        return False
