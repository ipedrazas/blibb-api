#
#
#   oimodels.py
#
#

from flask import current_app
from datetime import datetime

# from bson.objectid import ObjectId
from pymongo import Connection
from bson.objectid import ObjectId
from API.oiapp.base import Base
from API.utils import get_config_value, is_valid_id, queue_ducksboard_delta
from API.mail import send_invitations
from hashlib import sha1
import redis
import json
from API.oiapp.parse import do_push


class Audit(Base):

    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['audits']

    @classmethod
    def push(cls, email, oiid, subscribers, device):
        if is_valid_id(oiid):
            now = datetime.now()
            cls.objects.insert({'t': now, 'o': ObjectId(oiid), 'u': email, 'a': 'p', 's': subscribers, 'd': device})
            queue_ducksboard_delta('80399')
            queue_ducksboard_delta('81014')

    @classmethod
    def login(cls, email, device):
        now = datetime.utc()
        cls.objects.insert({'t': now, 'u': email, 'a': 'l', 'd': device})
        queue_ducksboard_delta('81209')

    @classmethod
    def new_oi(cls, email, oiid, device):
        if is_valid_id(oiid):
            now = datetime.utc()
            cls.objects.insert({'t': now, 'u': email, 'o': oiid, 'a': 'n', 'd': device})
            queue_ducksboard_delta('81176')

    @classmethod
    def subscribe(cls, email, device, oiid):
        if is_valid_id(oiid):
            now = datetime.utc()
            cls.objects.insert({'t': now, 'u': email, 'o': ObjectId(oiid), 'a': 's', 'd': device})
            queue_ducksboard_delta('81296')

    @classmethod
    def signup(cls, email, device):
        now = datetime.utc()
        cls.objects.insert({'t': now, 'u': email, 'a': 'sp', 'd': device})
        queue_ducksboard_delta('80347')


class Oi(Base):

    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['ois']

    @classmethod
    def create(cls, owner, name, contacts, tags):
        ## check name
        oi_name = Oi.get({'name': name})
        tag_list = []
        if oi_name is None:
            oi = dict()
            oi['owner'] = owner
            now = datetime.utc()
            oi['created_at'] = now
            oi['name'] = name
            rnd_id = str(sha1(name + owner + str(now)).hexdigest())
            contacts_list = []
            if contacts is not None:
                    if ',' in contacts:
                        contacts_list = list(set(contacts.strip().lower().split(',')))
                    else:
                        contacts_list.append(contacts)
            oi['invited'] = contacts_list

            oi['channel'] = '%s-%s-%s' % (cls.parse_string(owner), cls.parse_string(name), rnd_id)
            oi['senders'] = [owner]
            oi['subscribers'] = [owner]

            if tags is not None:
                if ',' in tags:
                    tag_list = list(set(tags.lower().split(',')))
                else:
                    tag_list = list(set(tags.lower().split()))
            oi['tags'] = tag_list
            oi['_id'] = cls.objects.insert(oi)
            send_invitations(oi)
            return oi
        else:
            error = {'error': 'Oi with that name already exists'}
        return error

    @classmethod
    def parse_string(cls, buffer):
        buffer = buffer.replace('@', '-')
        buffer = buffer.replace(' ', '')
        buffer = buffer.replace('.', '')
        buffer = buffer.replace(',', '')
        buffer = buffer.replace('\'', '')
        return buffer

    @classmethod
    def can_push(cls, oiid, user):
        if is_valid_id(oiid):
            doc = cls.get({'_id': ObjectId(oiid)})
            return cls.in_senders(doc, user)
        return False

    @classmethod
    def in_senders(cls, doc, user):
        performers = doc.get('senders', None)
        if performers:
            if user['email'] in performers or user['username'] in performers:
                return True
        return False

    @classmethod
    def subscribe(cls, oiid, user):
        if is_valid_id(oiid):
            doc = cls.get({'_id': ObjectId(oiid)})
            guests = doc.get('invited', None)

            for u in guests:
                current_app.logger.info(doc)
                if u == user['email'] or u == user['username']:
                    cls.remove_user(guests, user)
                    doc['invited'] = guests
                    if user not in doc['senders']:
                        doc['senders'].append(user['username'])
                    if user not in doc['subscribers']:
                        doc['subscribers'].append(user['username'])
                    cls.objects.save(doc)
                    return True
        return False

    @classmethod
    def remove_user(cls, target_list, user):
        for u in target_list:
            if user['email'] in target_list:
                target_list.remove(user['email'])
            if user['username'] in target_list:
                target_list.remove(user['username'])

    @classmethod
    def push(cls, doc):
        channel = doc['channel']
        name = doc['name']
        cls.objects.update({'_id': doc['_id']}, {"$inc": {'pushes': 1}, '$set': {"last_push": datetime.now()}})
        return do_push(name, channel)


class User(Base):
    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['users']

    @classmethod
    def inc_push(cls, username):
        if username:
            cls.objects.update({'username': username}, {"$inc": {'pushes': 1}, '$set': {"last_push": datetime.now()}})

    @classmethod
    def regiser_device(cls, username, device):
        if username:
            cls.objects.update({'username': username}, {'$addToSet': {'device': device}})
            return True
        return False

    @classmethod
    def remove_device(cls, username, device):
        if username:
            cls.objects.update({'username': username}, {'$pull': {'device': device}})
            return True
        return False

    @classmethod
    def grant_role(cls, username, role):
        if username:
            cls.objects.update({'username': username}, {'$addToSet': {'role': role}})
            return True
        return False

    @classmethod
    def remove_role(cls, username, role):
        if username:
            cls.objects.update({'username': username}, {'$pull': {'role': role}})
            return True
        return False

    @classmethod
    def create(cls, username, password, email, device=None):
        # check if the user is nt registered already
        u = User.get({'username': username})
        if u is None:
            user = dict()
            user['username'] = username
            user['email'] = email
            user['created_at'] = datetime.utc()
            salt = sha1(username + str(datetime.utc())).hexdigest()
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
        banned = ['password', 'salt', '_id']
        obj = cls.to_dict(obj)
        for b in banned:
            if b in obj:
                del obj[b]
        return obj

    @classmethod
    def change_password(cls, username, password, old_password):
        stUser = cls.get({'username': username.strip()})
        if stUser is not None:
            shPwd = sha1(stUser['salt'] + old_password)
            if stUser['password'] == shPwd.hexdigest():
                shPwd = sha1(stUser['salt'] + password)
                stUser['password'] = shPwd.hexdigest()
                stUser['last_access'] = datetime.utc()
                cls.objects.save(stUser)
                user = cls.to_safe_dict(stUser)
                user['key'] = cls.set_key(stUser)
                return user
        return False

    @classmethod
    def authenticate(cls, username, password):
        stUser = cls.get({'$or': [{'username': username.strip()}, {'email': username.strip()}]})
        if stUser is not None:
            shPwd = sha1(stUser['salt'] + password)
            if stUser['password'] == shPwd.hexdigest():
                stUser['last_access'] = datetime.utc()
                cls.objects.save(stUser)
                user = cls.to_safe_dict(stUser)
                user['key'] = cls.set_key(stUser)
                return user
        return False

    @classmethod
    def get_by_name(self, username):
        doc = self.get_object({'username': username}, {'password': 0, 'salt': 0})
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
        userkey = sha1(user['email'] + user['last_access'] + str(datetime.utc())).hexdigest()
        r.set(userkey, json.dumps(user))
        # expire = get_config_value('EXPIRE')
        # r.expire(userkey, expire)
        return userkey

    @classmethod
    def get_redis(self):
        return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
