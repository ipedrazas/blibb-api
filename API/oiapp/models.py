#
#
#   oimodels.py
#
#


from datetime import datetime

# from bson.objectid import ObjectId
from pymongo import Connection
from API.oiapp.base import Base
from API.utils import get_config_value
from hashlib import sha1
import redis
import json


class Oi(Base):

    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['ois']

    @classmethod
    def create(cls, owner, name, contacts):
        oi = dict()
        oi['owner'] = owner
        oi['created_at'] = datetime.utcnow()
        oi['channel'] = owner + '-' + name + '-' + str(sha1(name + owner + str(datetime.utcnow())).hexdigest())
        contacts_list = []
        if contacts is not None:
                if ',' in contacts:
                    contacts_list = list(set(contacts.lower().split(',')))
        oi['invited'] = contacts_list
        oi['_id'] = cls.objects.insert(oi)
        return oi


class User(Base):
    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['users']

    @classmethod
    def regiser_device(cls, email, device):
        if email:
            cls.objects.update({'email': email}, {'$addToSet': {'device': device}})
            return True
        return False

    @classmethod
    def remove_device(cls, email, device):
        if email:
            cls.objects.update({'email': email}, {'$pull': {'device': device}})
            return True
        return False

    @classmethod
    def grant_role(cls, email, role):
        if email:
            cls.objects.update({'email': email}, {'$addToSet': {'role': role}})
            return True
        return False

    @classmethod
    def remove_role(cls, email, role):
        if email:
            cls.objects.update({'email': email}, {'$pull': {'role': role}})
            return True
        return False

    @classmethod
    def create(cls, email, password, device=None):
        # check if the user is nt registered already
        u = User.get({'email': email})
        if u is None:
            user = dict()
            user['email'] = email
            user['created_at'] = datetime.utcnow()
            salt = sha1(email + str(datetime.utcnow())).hexdigest()
            user['salt'] = salt
            user['password'] = sha1(salt + password).hexdigest()
            user['role'] = ['user']
            if device:
                user['devices'] = [device]
            user['_id'] = cls.objects.insert(user)
            return user
        else:
            return {'error': 'User already exists'}

    @classmethod
    def to_safe_dict(cls, obj):
        obj = cls.to_dict(obj)
        del obj['password']
        del obj['salt']
        return obj

    @classmethod
    def authenticate(cls, email, password):
        stUser = cls.get({'email': email.strip()})
        if stUser is not None:
            shPwd = sha1(password + stUser['s'])
            if stUser['p'] == shPwd.hexdigest():
                stUser['la'] = datetime.utcnow()
                cls.objects.save(stUser)
                user = cls.to_safe_dict(stUser)
                key = cls.set_key(user)
                user['key'] = key
                return user
        return False

    @classmethod
    def get_by_name(self, username):
        doc = self.get_object({'n': username}, {'p': 0, 's': 0})
        return self.flat_object(doc)

    @classmethod
    def get_user(cls, key):
        r = cls.get_redis()
        return r.get(key)

    @classmethod
    def logout(self, key):
        r = self.get_redis()
        return r.delete(key)

    @classmethod
    def set_key(cls, user):
        r = cls.get_redis()
        userkey = sha1(user['username'] + user['id'] + str(datetime.utcnow())).hexdigest()
        r.set(userkey, json.dumps(user))
        expire = get_config_value('EXPIRE')
        r.expire(userkey, expire)
        return userkey

    @classmethod
    def get_redis(self):
        return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
