#
#
#   User.py
#
#


from API.contenttypes.picture import Picture
from datetime import datetime

from pymongo import Connection
import hashlib
import redis
import json

conn = Connection()
db = conn['blibb']
objects = db['users']


class User(object):

    @classmethod
    def get_redis(self):
        return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    @classmethod
    def create(self, name, email, password, code):
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

    @classmethod
    def authenticate(self, user, password):
        stUser = objects.find_one({'$or': [{'e': user.strip()}, {'n':user.strip()}]})
        if stUser is not None:
            shPwd = hashlib.sha1(password + stUser['s'])
            print shPwd.hexdigest()
            print stUser['p']
            if stUser['p'] == shPwd.hexdigest():
                if 'i' in stUser:
                    return self.setKey(str(stUser['_id']), stUser['n'], stUser['e'], stUser['i'])
                else:
                    return self.setKey(str(stUser['_id']), stUser['n'], stUser['e'])
        return False

    @classmethod
    def setKey(self, user_id, user_name, email, user_image=None):
        r = self.get_redis()
        userkey = hashlib.sha1(user_name + user_id + str(datetime.utcnow())).hexdigest()
        user = self.get_by_name(user_name)
        r.set(userkey, json.dumps(user))
        expire = 3600
        r.expire(userkey, expire)

        return userkey

    @classmethod
    def get_object(self, filter, fields):
        return objects.find_one(filter, fields)

    @classmethod
    def get_by_name(self, username):
        doc = self.get_object({'n': username}, {'p': 0, 's': 0})
        return self.flat_object(doc)

    @classmethod
    def add_picture(self, filter, picture_id):
        if picture_id is not None:
            p = Picture()
            image = p.dumpImage(picture_id)
            objects.update(filter, {"$set": {'i': image}}, True)
            return picture_id
        return 'error'

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
            if 'i' in doc:
                    img = doc['i']
                    buf['image'] = str(img['id'])
            if 'a' in doc:
                    buf['status'] = doc['a']

        return buf
