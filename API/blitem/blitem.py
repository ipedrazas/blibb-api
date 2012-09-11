#
#
#   blitem.py
#
#

from flask import current_app
from datetime import datetime

from bson.objectid import ObjectId
from pymongo import Connection

from API.control.control_type import ControlType
from API.blibb.blibb import Blibb
from API.comment.comment import Comment
from API.contenttypes.song import Song

from API.error import Message
from API.utils import is_valid_id, send_url, queue_twitter_resolution, get_config_value
import re
from blinker import signal


conn = Connection(get_config_value('MONGO_URL'))
db = conn['blibb']
objects = db['blitems']


def do_post_process(item):
    # print 'signal:' + str(item)
    # current_app.logger.info(str(item))
    object_id = str(item['_id'])
    items = item['i']
    for element in items:
        typex = element['t']
        if ControlType.is_url(typex):
            send_url(object_id, element['v'])
        elif ControlType.is_twitter(typex):
            queue_twitter_resolution(object_id, element['v'])


post_process = signal('item-post-process')
post_process.connect(do_post_process)


class Blitem(object):

    @classmethod
    def remove(self, filter):
        if filter is not None:
            objects.update(filter, {'$set': {'st': 'del'}})

    @classmethod
    def insert(self, blibb_id, user, items, tags=None):
        tag_list = []
        if is_valid_id(blibb_id):
            bid = ObjectId(blibb_id)
            b = Blibb.get_object({'_id': bid}, {'s': 1})
            bs = b['s']
            if tags is not None:
                if ',' in tags:
                    tag_list = list(set(tags.lower().split(',')))
                else:
                    tag_list = list(set(tags.lower().split()))
                for t in tag_list:
                    Blibb.add_tag(blibb_id, t)

            now = datetime.utcnow()
            doc = {"b": bid, "u": user, "bs": bs, "c": now, "i": items, 'tg': tag_list, 'st': 'active'}
            newId = objects.insert(doc)
            post_process.send(doc)
            return str(newId)
        else:
            return Message.get('id_not_valid')

    @classmethod
    def update(self, item_id, blibb_id, user, items, tags=None):
        tag_list = []
        if is_valid_id(blibb_id) and is_valid_id(item_id):
            # bid = ObjectId(blibb_id)
            # b = Blibb.get_object({'_id': bid}, {'s': 1})
            # bs = b['s']
            if tags is not None:
                if ',' in tags:
                    tag_list = list(set(tags.lower().split(',')))
                else:
                    tag_list = list(set(tags.lower().split()))
                for t in tag_list:
                    Blibb.add_tag(blibb_id, t)

            # now = datetime.utcnow()
            doc = {"_id": item_id, "b": blibb_id, "i": items}
            objects.update({"_id": ObjectId(item_id)}, {'$set': {"i": items}})
            post_process.send(doc)
            return item_id
        else:
            return Message.get('id_not_valid')

    @classmethod
    def save(self, item):
        objects.save(item)

    @classmethod
    def get(self, filter, fields={}):
        doc = objects.find_one(filter)
        return doc

    @classmethod
    def get_item(self, filter, fields={}):
        doc = self.get(filter)
        doc['_id'] = str(doc['_id'])
        doc['b'] = str(doc['b'])
        date = doc['c']
        doc['c'] = date.strftime("%d/%m/%y")
        return doc

    def getById(self, obj_id):
        if is_valid_id(obj_id):
            return self.getItem({'_id': ObjectId(obj_id)})
        return Message.get('id_not_valid')

    @classmethod
    def flat_object(self, doc, attributes={}):
        blitem = dict()
        fields = []
        elements = []
        if doc is not None:
            blitem_id = str(doc.get('_id', ''))
            blitem['id'] = blitem_id
            blitem['parent'] = str(doc.get('b', ''))
            blitem['num_comments'] = doc.get('cc', '')
            i = doc.get('i', False)
            if i:
                for r in i:
                    s = r.get('s', '')
                    t = r.get('t', '')
                    field = t + '-' + s
                    if field not in fields:
                        fields.append(field)
                    blitem[r['s']] = r['cv'] if 'cv' in r else r['v']
                blitem['fields'] = fields
                if attributes.get('elements', False):
                    blitem['elements'] = elements
            if attributes.get('tags', False):
                blitem['tags'] = doc.get('tg', '')
            if attributes.get('comments', False):
                blitem['comments'] = self.get_comments(blitem_id)
        return blitem

    @classmethod
    def get_flat(self, obj_id):
        doc = self.get_item({'_id': ObjectId(obj_id)})
        return self.flat_object(doc, {'tags': True, 'comments': True})

    @classmethod
    def get_comments(self, obj_id):
        return Comment.get_comments_by_id(obj_id)

    @classmethod
    def get_items_page(self, filter, fields, page=1):
        PER_PAGE = 20
        docs = objects.find(filter, fields).sort("c", -1).skip(PER_PAGE * (page - 1)).limit(PER_PAGE)
        return docs

    @classmethod
    def get_all_items(self, blibb_id, page, attributes={'tags': True, 'comments': True}, flat=True):
        if is_valid_id(blibb_id):
            docs = self.get_items_page({'b': ObjectId(blibb_id)}, {'i': 1, 'tg': 1, 'b': 1}, page)
            result = dict()
            blitems = []
            for d in docs:
                if flat:
                    blitems.append(self.flat_object(d, attributes))
                else:
                    blitems.append(d)
            result['b_id'] = blibb_id
            result['count'] = len(blitems)
            result['items'] = blitems

            return result
        return Message.get('id_not_valid')

    def get_items_by_tag(self, blibb_id, tag):
        if is_valid_id(blibb_id):
            docs = self.get_items_page({'b': ObjectId(blibb_id), 'tg': tag}, {'i': 1, 'tg': 1, 'b': 1})
            result = dict()
            blitems = []
            attributes = {'tags': True}
            for d in docs:
                blitems.append(self.flat_object(d, attributes))

            result['count'] = len(blitems)
            result['items'] = blitems

            return result
        return Message.get('id_not_valid')

    @classmethod
    def get_blitem_item(self, key, value, labels):
        value = value.strip()
        slug = key[3:]
        typex = key[:2]
        blitem = {}
        blitem['t'] = typex
        blitem['s'] = slug
        if ControlType.is_multitext(typex):
            value = ControlType.autoP(value)
        elif ControlType.isMp3(typex):
            song = Song()
            song.load(value)
            value = song.dumpSong()
        elif ControlType.is_image(typex):
            value = ObjectId(value)
        elif ControlType.is_date(typex):
            # TODO: convert dates to MongoDates
            # and back
            value = value
        elif ControlType.is_twitter(typex):
            value = re.sub('[!@#$]', '', value)

        blitem['v'] = value
        blitem['l'] = labels.get(slug)
        return blitem

    @classmethod
    def get_blitem_from_dict(self, items, labels):
        blitem = []
        for key, value in items.iteritems():
            blitem.append(self.get_blitem_item(key, value, labels))

        return blitem

    @classmethod
    def bulk_insert(self, blibb_id, user, items, tags=None):
        if is_valid_id(blibb_id):
            bid = ObjectId(blibb_id)
            b = Blibb.get_object({'_id': bid}, {'s': 1, 'u': 1, 't.i.n': 1, 't.i.s': 1})
            blibb_slug = b.get('s')
            labels = Blibb.get_labels(b.get('t'))
            count = 0
            for item in items:
                now = datetime.utcnow()
                i = self.get_blitem_from_dict(item, labels)
                doc = {"b": bid, "u": user, "bs": blibb_slug, "c": now, "i": i}
                objects.insert(doc)
                count = count + 1

            return str(count) + 'elements added'
        else:
            return Message.get('id_not_valid')

    @classmethod
    def get_blitem_from_request(self, key, value, control):
        value = value.strip()
        blitem = {}
        blitem['t'] = control['type']
        blitem['s'] = control['slug']

        if ControlType.is_multitext(control['type']):
            value = ControlType.autoP(value)
        elif ControlType.is_image(control['type']):
            value = ObjectId(value)
        elif ControlType.is_date(control['type']):
            # TODO: convert dates to MongoDates
            # and back
            value = value
        elif ControlType.is_twitter(control['type']):
            value = re.sub('[!@#$]', '', value)

        blitem['v'] = value
        blitem['l'] = control['name']
        return blitem

    @classmethod
    def get_items_from_request(self, controls, request):
        bitems = []
        for key, value in request.form.iteritems():
            current_app.logger.info(key + ' ' + str(controls.keys()))
            if key in controls.keys():
                control = controls.get(key)
                current_app.logger.info(control)
                elem = self.get_blitem_from_request(key, value, control)
                bitems.append(elem)
        return bitems

    @classmethod
    def post_process(self, obj_id, items):
        for blitem in items:
            # print blitem
            typex = blitem['t']
            if ControlType.is_url(typex):
                send_url(obj_id, blitem['v'])
            elif ControlType.is_twitter(typex):
                queue_twitter_resolution(obj_id, blitem['v'])

    @classmethod
    def can_write(cls, user, blitem_id):
        if is_valid_id(blitem_id):
            doc = cls.get({'_id': ObjectId(blitem_id)})
            blibb_id = str(doc['b'])
            current_app.logger.info('can_write' + user + ' ' + blibb_id)
            return Blibb.can_write(user, '', blibb_id)
        return False

    @classmethod
    def vote_up(cls, item_id, user):
        return cls.vote(item_id, user, 1, 'm.v.u')

    @classmethod
    def vote_down(cls, item_id, user):
        return cls.vote(item_id, user, -1, 'm.v.d')

    @classmethod
    def vote(cls, item_id, user, vote, att):
        if is_valid_id(item_id):
            current_app.logger.info(item_id + ' ' + user + ' ' + str(vote) + ' ' + att)
            elem = db['votes'].find_one({'i': ObjectId(item_id), 'u': user})
            if elem is None:
                objects.update({"_id": ObjectId(item_id)}, {"$inc": {att: vote}})
                db['votes'].insert({'u': user, 'i': ObjectId(item_id), 'v': vote})
                return {'vote': 'ok'}
            else:
                return {'error': 'User has already voted'}
        return {'error': 'Object not valid'}

    @classmethod
    def increase_comment_counter(cls, item_id):
        if is_valid_id(item_id):
            objects.update({"_id": ObjectId(item_id)}, {"$inc": {'nc': 1}})
