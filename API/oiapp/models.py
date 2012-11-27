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
import re
from API.oiapp.parse import do_push


class Audit(Base):

    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['audits']

    @classmethod
    def push(cls, user, oiid, device, subscribers):
        if is_valid_id(oiid):
            now = datetime.now()
            cls.objects.insert({'t': now, 'o': ObjectId(oiid), 'u': user, 'a': 'p', 's': subscribers, 'd': device})
            # Ois sent
            queue_ducksboard_delta('80399')
            # Ois per day
            queue_ducksboard_delta('81014')
            num_push = len(subscribers)
            # Ois received
            queue_ducksboard_delta('90195', num_push)


    @classmethod
    def login(cls, user, device):
        now = datetime.now()
        cls.objects.insert({'t': now, 'u': user, 'a': 'l', 'd': device})
        queue_ducksboard_delta('81209')

    @classmethod
    def new_oi(cls, user, oiid, device):
        if is_valid_id(oiid):
            now = datetime.now()
            cls.objects.insert({'t': now, 'u': user, 'o': oiid, 'a': 'n', 'd': device})
            queue_ducksboard_delta('81176')

    @classmethod
    def subscribe(cls, user, device, oiid):
        if is_valid_id(oiid):
            now = datetime.now()
            cls.objects.insert({'t': now, 'u': user, 'o': ObjectId(oiid), 'a': 's', 'd': device})
            queue_ducksboard_delta('81296')

    @classmethod
    def unsubscribe(cls, user, device, oiid):
        if is_valid_id(oiid):
            now = datetime.now()
            cls.objects.insert({'t': now, 'u': user, 'o': ObjectId(oiid), 'a': 'u'})
            queue_ducksboard_delta('92094')

    @classmethod
    def delete(cls, user, device, oiid):
        if is_valid_id(oiid):
            now = datetime.now()
            cls.objects.insert({'t': now, 'u': user, 'o': ObjectId(oiid), 'a': 'd'})
            queue_ducksboard_delta('92093')

    @classmethod
    def signup(cls, user, device):
        now = datetime.now()
        cls.objects.insert({'t': now, 'u': user, 'a': 'sp', 'd': device})
        queue_ducksboard_delta('80347')

    @classmethod
    def fav(cls, user, device, oiid):
        now = datetime.now()
        cls.objects.insert({'t': now, 'u': user, 'o': ObjectId(oiid), 'a': 'f', 'd': device})
        queue_ducksboard_delta('93345')

    @classmethod
    def unfav(cls, user, device, oiid):
        now = datetime.now()
        cls.objects.insert({'t': now, 'u': user, 'o': ObjectId(oiid),'a': 'uf', 'd': device})
        queue_ducksboard_delta('93346')



class Oi(Base):

    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['ois']

    @classmethod
    def process_invitations(cls, oi):
        invitations = oi['invited']
        invited = []
        current_app.logger.info('invitations ' + str(invitations))
        for p in invitations:
            u = User.is_oi_user(p)
            current_app.logger.info('invited: ' + str(p))
            current_app.logger.info('user: ' + str(u))
            if u:
                if u['username'] not in oi['subscribers']:
                    oi['subscribers'].append(u['username'])
                if u['username'] not in oi['senders']:
                    oi['senders'].append(u['username'])
            else:
                invited.append(p)

        oi['invited'] = invited
        cls.objects.save(oi)
        send_invitations(oi)


    @classmethod
    def create(cls, owner, name, contacts, tags):
        ## check name
        oi_name = Oi.get({'name': name, 'owner': owner, 'del': {'$exists': False}})
        tag_list = []
        if oi_name is None:
            oi = dict()
            oi['owner'] = owner
            now = datetime.now()
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
            oi['push'] = {'when': '', 'who': ''}
            oi['sent'] = 0
            oi['pushes'] = 0
            oi['channel'] = '%s-%s-%s' % (cls.parse_string(owner), cls.parse_string(name), rnd_id)
            oi['senders'] = [owner]
            oi['subscribers'] = [owner]

            if tags is not None:
                if ',' in tags:
                    tag_list = list(set(tags.lower().split(',')))
                else:
                    tag_list = list(set(tags.lower().split()))
            oi['tags'] = tag_list
            new_id = cls.objects.insert(oi)
            current_app.logger.info(str(oi))
            if is_valid_id(new_id):
                oi['_id'] = new_id
                cls.process_invitations(oi)
                return oi
            else:
                error = {'error': 'Error creating the Oi'}
        else:
            error = {'error': 'Oi with that name already exists'}
        return error

    @classmethod
    def parse_string(cls, buffer):
        return re.sub('[^0-9a-zA-Z]', '', buffer)

    @classmethod
    def can_push(cls, oiid, user):
        if is_valid_id(oiid):
            doc = cls.get({'_id': ObjectId(oiid)})
            return cls.in_senders(doc, user)
        return False

    @classmethod
    def in_senders(cls, doc, user):
        performers = doc.get('senders', None)
        if performers and user:
            if user['email'] in performers or user['username'] in performers:
                return True
        return False

    @classmethod
    def subscribe(cls, oiid, user):
        doc = cls.get({'_id': ObjectId(oiid)})
        current_app.logger.info("Doc to subscribe" + str(doc))
        guests = doc.get('invited', None)
        username = user['username']
        for guest in guests:
            if guest in user['sub_email']:
                cls.remove_user(guests, user)
                doc['invited'] = guests
                if username not in doc['senders']:
                    doc['senders'].append(username)
                if username not in doc['subscribers']:
                    doc['subscribers'].append(username)
                cls.objects.save(doc)
                return True

    @classmethod
    def unsubscribe(cls, oiid, user):
        doc = cls.get({'_id': ObjectId(oiid)})
        if doc:
            if user in doc['subscribers']:
                doc['subscribers'].remove(user)
            if user in doc['senders']:
                doc['senders'].remove(user)
            cls.objects.save(doc)
            return True
        return False

    @classmethod
    def remove_user(cls, target_list, user):
        if 'sub_emails' in user:
            sub_emails = user['sub_email']
            for e in sub_emails:
                if e in target_list:
                    target_list.remove(e)

    @classmethod
    def push(cls, doc, user):
        channel = doc['channel']
        name = doc['name']
        username = user['username']
        last_push = {"when":  datetime.now(), "who": username}
        total_push = len(doc['subscribers'])
        cls.objects.update({'_id': doc['_id']}, {"$inc": {'pushes': 1, 'sent': total_push}, '$set': {"push": last_push}})
        push = do_push(name, channel, username)
        User.inc_push(username)
        return push

    @classmethod
    def update(cls, oiid, attribute):
        if is_valid_id(oiid):
            cls.objects.update({'_id': ObjectId(oiid), 'del': {'$exists': False}}, {'$set': {attribute['name']: attribute['value']}})

    @classmethod
    def fav(cls, oiid, user):
        doc = cls.get({'_id': ObjectId(oiid), 'subscribers': user})
        current_app.logger.info(str(doc))
        if doc:
            if user not in doc.get('fav',[]):
                doc['fav'].append(user)
                cls.objects.save(doc)
                return True
        return False

    @classmethod
    def unfav(cls, oiid, user):
        doc = cls.get({'_id': ObjectId(oiid), 'fav': user})
        if doc:
            if user in doc['fav']:
                doc['fav'].remove(user)
                cls.objects.save(doc)
                return True
        return False

class User(Base):
    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['users']


    @classmethod
    def is_oi_user(cls, email):
        u = cls.get({'$or': [{'sub_email': email.strip()}, {'username': email.strip()}]})
        if u is not None:
            return u
        return False


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
    def add_subscrived_email(cls, username, email):
        if username:
            cls.objects.update({'username': username}, {'$addToSet': {'sub_email': email}})
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
        if cls.is_oi_user(username) or cls.is_oi_user(email):
            return {'error': 'User already exists'}
        else:
            user = dict()
            user['username'] = username
            user['email'] = email
            user['sub_email'] = [email]
            user['created_at'] = datetime.now()
            salt = sha1(username + str(datetime.now())).hexdigest()
            user['salt'] = salt
            user['password'] = sha1(salt + password).hexdigest()
            user['role'] = ['user']
            if device:
                user['devices'] = [device]
            user['_id'] = cls.objects.insert(user)
            return user


    @classmethod
    def to_safe_dict(cls, obj):
        banned = ['password', 'salt', '_id']
        obj = cls.to_dict(obj)
        if obj:
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
                stUser['last_access'] = datetime.now()
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
                stUser['last_access'] = datetime.now()
                cls.objects.save(stUser)
                user = cls.to_safe_dict(stUser)
                user['key'] = cls.set_key(stUser)
                return user
        return False

    @classmethod
    def get_by_name(self, username):
        doc = self.get({'username': username}, {'password': 0, 'salt': 0})
        return self.to_safe_dict(doc)

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
        userkey = sha1(user['email'] + user['last_access'] + str(datetime.now())).hexdigest()
        r.set(userkey, json.dumps(user))
        return userkey

    @classmethod
    def get_redis(self):
        return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)



