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
from API.control.bcontrol import BControl
from API.comment.comment import Comment
from API.contenttypes.song import Song

from API.error import Message
import API.utils as utils
import re


conn = Connection()
db = conn['blibb']
objects = db['blitems']


class Blitem(object):

    def __init__(self):
        pass

    @classmethod
    def insert(self, blibb_id, user, items, tags=None):
        tag_list = []
        if utils.is_valid_id(blibb_id):
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
            doc = {"b": bid, "u": user, "bs": bs, "c": now, "i": items, 'tg': tag_list}
            newId = objects.insert(doc)
            return str(newId)
        else:
            return Message.get('id_not_valid')

    def update(self, attr, value):
        self.objects.update(
                {u"_id": ObjectId(self.id)}, {attr: value}
            )

    @classmethod
    def save(self, item):
        objects.save(item)

    @classmethod
    def get_item(self, filter, fields={}):
        doc = objects.find_one(filter)
        return doc

    def getById(self, obj_id):
        if utils.is_valid_id(obj_id):
            return self.getItem({'_id': ObjectId(obj_id)})
        return Message.get('id_not_valid')

    @classmethod
    def flat_object(self, doc, attributes):
        blitem = dict()
        fields = []
        elements = []
        current_app.logger.info(str(attributes))
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
                    blitem[r['s']] = r['v']
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
        doc = objects.find_one({'_id': ObjectId(obj_id)})
        return self.flat_object(doc)

    @classmethod
    def get_comments(self, obj_id):
        c = Comment()
        cs = c.getCommentsById(obj_id)
        return cs

    @classmethod
    def get_items_page(self, filter, fields, page=1):
        PER_PAGE = 20
        docs = objects.find(filter, fields).sort("c", -1).skip(PER_PAGE * (page - 1)).limit(PER_PAGE)
        return docs

    @classmethod
    def get_all_items(self, blibb_id, page, attributes={}, flat=True):
        if utils.is_valid_id(blibb_id):
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

    def getItemsByTag(self, blibb_id, tag):
        if utils.is_valid_id(blibb_id):
            docs = self.get_items_page({'b': ObjectId(blibb_id), 'tg': tag}, {'i': 1, 'tg': 1, 'b': 1})
            result = dict()
            blitems = []
            for d in docs:
                blitems.append(self.flat_object(d))

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
        if BControl.isMultitext(typex):
            value = BControl.autoP(value)
        elif BControl.isMp3(typex):
            song = Song()
            song.load(value)
            value = song.dumpSong()
        elif BControl.isImage(typex):
            value = ObjectId(value)
        elif BControl.isDate(typex):
            # TODO: convert dates to MongoDates
            # and back
            value = value
        elif BControl.isTwitter(typex):
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
        if utils.is_valid_id(blibb_id):
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
    def get_blitem_from_request(self, key, value, labels):
        value = value.strip()
        slug = key[3:]
        typex = key[:2]
        blitem = {}
        blitem['t'] = typex
        blitem['s'] = slug
        if BControl.isMultitext(typex):
            value = BControl.autoP(value)
        # elif BControl.isMp3(typex):
        #     song = Song()
        #     song.load(value)
        #     value = song.dumpSong()
        elif BControl.isImage(typex):
            value = ObjectId(value)
        elif BControl.isDate(typex):
            # TODO: convert dates to MongoDates
            # and back
            value = value
        elif BControl.isTwitter(typex):
            value = re.sub('[!@#$]', '', value)

        blitem['v'] = value
        blitem['l'] = labels.get(slug)
        return blitem

    @classmethod
    def get_items_from_request(self, labels, request):
        bitems = []
        for key, value in request.form.iteritems():
            if '-' in key:
                elem = self.get_blitem_from_request(key, value, labels)
                bitems.append(elem)
        return bitems

    @classmethod
    def postProcess(self, obj_id, items):
        for blitem in items:
            # print blitem
            typex = blitem['t']
            if ControlType.is_url(typex):
                utils.sendUrl(obj_id, blitem['v'])
            if ControlType.is_twitter(typex):
                utils.queueTwitterResolution(obj_id, blitem['v'])
