#
#
#   blibb.py
#
#


from flask import jsonify, current_app
from datetime import datetime
from string import digits, ascii_letters
from random import sample

from bson.objectid import ObjectId
from pymongo import Connection
from API.contenttypes.picture import Picture
from API.template.ctrl_template import ControlTemplate
from API.om.acl import ACL
from API.error import Message
import hashlib
from API.utils import is_valid_id, date_to_str, get_config_value


conn = Connection(get_config_value('MONGO_URL'))
db = conn['blibb']
objects = db['blibbs']
NUM_CHARS = get_config_value('NUM_CHARS')


class Blibb(object):

    @classmethod
    def update_view(cls, objectid, user, view, html):
        field = 't.v.%s.rb' % (view)
        objects.update({'_id': ObjectId(objectid)},
                       {'$set': {field: html, 'lm': user}})

    @classmethod
    def to_dict(self, obj):
        if obj is not None and not isinstance(obj, unicode):
            for key, value in obj.items():
                if isinstance(value, ObjectId):
                    obj[key] = str(value)
                elif isinstance(value, datetime):
                    obj[key] = value.strftime("%d/%m/%y")
                elif isinstance(value, (dict)):
                    obj[key] = self.to_dict(value)
                elif isinstance(value, (list)):
                    t = []
                    for elem in value:
                        t.append(self.to_dict(elem))
                    obj[key] = t
                else:
                    obj[key] = value

        return obj

    @classmethod
    def save(self, object):
        objects.save(object)

    @classmethod
    def insert(self, user, name, slug, desc, template_id, image,
               read_access, write_access):
        if is_valid_id(template_id):
            template = ControlTemplate.get_object(
                {'_id': ObjectId(template_id)})
            items = template['i']
            fields = []
            for item in items:
                fields.append(item['s'])
            now = datetime.utcnow()
            acl = dict()
            acl['read'] = read_access
            acl['write'] = write_access
            num = int(NUM_CHARS)
            url_id = "".join(sample(digits + ascii_letters, num))
            doc = {"n": name, "s": slug, "d": desc, "u": user, "c": now,
                   "t": template, "img": image, 'a': acl, 'f': fields,
                   'at': slug, 'st': {'v': 0}, 'si': url_id}

            newId = objects.insert(doc)
            return str(newId)

    def get_template(self, obj_id):
        if is_valid_id(obj_id):
            template = self.get_object({'_id': ObjectId(obj_id)}, {'t': 1})
            return jsonify(self.flat_object(template))
        else:
            return Message.get('id_not_valid')

    @classmethod
    def get_labels(self, t):
        labels = dict()
        i = t['i']
        for r in i:
            labels[r['s']] = r['n']
        return labels

    @classmethod
    def get_label_from_template(self, obj_id):
        if is_valid_id(obj_id):
            result = self.get_object({'_id': ObjectId(obj_id)},
                                     {'t.i.n': 1, 't.i.s': 1})
            if result is not None:
                return self.get_labels(result['t'])
            else:
                return {'count': 0}
        else:
            return {'error': 'Object id not valid'}

    @classmethod
    def get_template_view(self, obj_id):
        if is_valid_id(obj_id):
            fields = {'t.v': 1, 'n': 1, 'd': 1, 'c': 1, 'u': 1, 'tg': 1,
                      's': 1, 'img': 1, 'ni': 1, 'st': 1}
            res = self.get_object({'_id': ObjectId(obj_id)}, fields)
            if '_id' in res:
                return self.flat_object(res)

    @classmethod
    def get_fields_from_template(cls, template):
        fields = []
        print template
        items = template['i']
        for item in items:
            fields.append(
                {'field': item['s'], 'type': item['tx'], 'order': item['o']}
            )

    @classmethod
    def flat_object(self, doc):
        buf = dict()
        if doc:
            buf['id'] = str(doc['_id'])
            if 't' in doc:
                buf['template'] = doc['t']
            if 'f' in doc:
                buf['fields'] = doc['f']
            if 'n' in doc:
                buf['name'] = doc['n']
            if 'd' in doc:
                buf['description'] = doc['d']
            if 'c' in doc:
                buf['date'] = date_to_str(doc['c'])
            if 'u' in doc:
                buf['owner'] = doc['u']
            if 's' in doc:
                buf['slug'] = doc['s']
            if 'ni' in doc:
                buf['num_items'] = doc.get('ni', 0)
            if 'st' in doc:
                stats = doc.get('st')
                nv = {'num_views': stats.get('v', 0)}
                nw = {'num_writes': stats.get('nw', 0)}
                ni = {'num_items': stats.get('ni', 0)}
                buf['stats'] = [nv, nw, ni]
            if 'a' in doc:
                buf['access'] = {
                    'read': ACL.get_access(doc.get('a').get('read')),
                    'write': ACL.get_access(doc.get('a').get('write'))
                }
            if 'img' in doc:
                img = doc['img']
                if 'id' in img:
                    buf['img'] = img['id']
                else:
                    buf['img'] = img
            if 'tg' in doc:
                buf['tags'] = doc['tg']
            if 'at' in doc:
                buf['app_token'] = doc['at']

        return buf

    @classmethod
    def get_by_id_params(self, obj_id, params):
        p = dict()
        if is_valid_id(obj_id):
            listparams = params.split(",")
            for param in listparams:
                p[param] = 1

            doc = self.get_object({'_id': ObjectId(obj_id)}, p)
            return self.flat_object(doc)
        return Message.get('id_not_valid')

    def stripslashes(self, s):
        r = s.replace('\\n', '')
        r = r.replace('\\t', '')
        r = r.replace('\\', '')
        return r

    @classmethod
    def get_blibbs(self, filter, fields, page=1):
        PER_PAGE = 20
        docs = objects.find(filter, fields).sort("c", -1).skip(
            PER_PAGE * (page - 1)).limit(PER_PAGE)
        return docs

    def get_by_user(self, username, page=1):
        r = self.get_blibbs(
            {'u': username, 'del': {'$ne': True}},
            {'t': 0}, page)
        rs = []
        count = 0
        for result in r:
            rs.append(self.flat_object(result))
            count += 1

        resp = dict()
        resp['count'] = count
        resp['results'] = rs
        return resp


    @classmethod
    def get_fields(self, obj_id):
        if is_valid_id(obj_id):
            doc = self.get_object({'_id': ObjectId(obj_id)}, {'t.i': 1})
            template = doc.get('t').get('i')
            fields = []
            for elem in template:
                fields.append(str(elem.get('tx')) + '-' + elem.get('s'))

            return fields

    @classmethod
    def get_webhooks(self, obj_id):
        if is_valid_id(obj_id):
            doc = self.get_object({u'_id': ObjectId(obj_id)}, {'wh': 1})
            whs = doc.get('wh', [])
            # return template
            webhooks = []
            for wh in whs:
                w = {
                    'action': wh.get('a'),
                    'callback': wh.get('u'),
                    'fields': wh.get('f')
                }
                webhooks.append(w)
            return webhooks

    @classmethod
    def inc_num_item(self, condition):
        self.increase_view(condition, 'ni')
        self.increase_view(condition, 'nw')

    @classmethod
    def increase_view(self, condition, field):
        objects.update(condition, {"$inc": {'st.' + field: 1}})

    @classmethod
    def add_tag(self, obj_id, tag):
        if is_valid_id(obj_id):
            objects.update(
                {'_id': ObjectId(obj_id)},
                {"$addToSet": {'tg': tag.lower()}},
                False)

    @classmethod
    def add_user_to_group(self, user, obj_id):
        if is_valid_id(obj_id):
            objects.update(
                {'_id': ObjectId(obj_id)},
                {"$addToSet": {'g': user}},
                False)

    @classmethod
    def add_webhook(self, object_id, webhook):
        if is_valid_id(object_id):
            self.objects.update(
                {'_id': ObjectId(object_id)},
                {'$pull': {'wh': {'a': webhook['a']}}}
            )
            self.objects.update(
                {'_id': ObjectId(object_id)},
                {'$addToSet': {'wh': webhook}})
        else:
            return Message.get('id_not_valid')

    @classmethod
    def get_object(self, filter={}, fields={}):
        return objects.find_one(filter, fields)

    @classmethod
    def get_by_slug(self, username, slug):
        doc = self.get_object({'u': username, 's': slug}, {'t': 0})
        return self.flat_object(doc)

    @classmethod
    def remove(self, filter):
        if filter is not None:
            objects.update(filter, {'$set': {'del': True}})

    @classmethod
    def can_write(self, user, app_token, blibb_id):
        """
            This method checks if a write operation can be performed.
            The method fallsback to the lower writing preference.
            First app_token, if it's valid, the method returns True.
            Second, the user is the owner.
            Third, the user belongs to a group with writing permission
            Last, it checks if WORLD has writing capabilities
        """

        if is_valid_id(blibb_id):
            blibb = self.get_object({'_id': ObjectId(blibb_id)}, {
                'a': 1, 'u': 1, 'g': 1, 'at': 1, 'n': 1, 'd': 1})
            current_app.logger.info(str(blibb))
            # atoken = blibb.get('at', 0)
            atoken = hashlib.sha1(blibb['n'] + blibb['d']).hexdigest()
            owner = blibb['u']
            acl = blibb.get('a', {})
            if atoken == app_token:
                return self.is_valid_token(atoken)
            if user == owner:
                return True
            if acl.get('write', 0) == 5:
                group = blibb['g']
                if user in group:
                    return True
            if acl.get('write', 0) == 11:
                return True
        # logging.warning('say')
        return False

    @classmethod
    def is_valid_token(self, token):
        """
            This will check if it's a valid production token
        """
        return True

    @classmethod
    def add_picture(self, filter, picture_id):
        if is_valid_id(picture_id):
            image = Picture.dump_image(picture_id)
            objects.update(filter, {"$set": {'img': image}})
            return picture_id
        return Message.get('id_not_valid')

    @classmethod
    def fork(self, object_id, username):
        if is_valid_id(object_id):
            doc = objects.find_one({'_id': ObjectId(object_id)})
            if doc:
                del doc['_id']
                fork = {}
                fork['fa'] = doc['u']
                fork['fd'] = doc['c']
                doc['f'] = fork
                doc['d'] = 'forked from %s/%s' % (doc['u'], doc['s'])
                doc['u'] = username
                doc['c'] = datetime.now()

                doc['st'] = {}

                objects.update(
                    {'_id': ObjectId(object_id)},
                    {"$inc": {'st.f': 1}}
                )

                return objects.insert(doc)

    @classmethod
    def get_controls_as_dict(self, template):
        if 'i' in template:
            cs = template['i']
            controls = dict()
            for control in cs:
                s = control['s']
                ctrl = dict()
                ctrl['type'] = control['tx']
                ctrl['name'] = control['n']
                ctrl['slug'] = control['s']
                controls[s] = ctrl
            return controls
        else:
            return None
