#
#
#   event.py
#
#


from datetime import datetime
from pymongo import Connection
from bson.objectid import ObjectId
from API.utils import is_valid_id
from flask import current_app

conn = Connection(current_app.config.get('MONGO_URL'))
db = conn['blibb']
objects = db['comments']


class Comment(object):

    @classmethod
    def insert(cls, parent, owner, text):
        now = datetime.utcnow()
        if is_valid_id(parent):
            doc = {"p": ObjectId(parent), "u": owner, "c": now, "t": text}
            newId = objects.insert(doc)
            return str(newId)

    @classmethod
    def get_comments_by_id(cls, obj_id):
        if is_valid_id(obj_id):
            docs = objects.find({'p': ObjectId(obj_id)}).sort("c", -1)
            ddocs = []
            for d in docs:
                ddocs.append(cls.flatObject(d))
            return ddocs
        else:
            return {'error': 'Object Id is not valid'}

    @classmethod
    def flatObject(self, comment):
        doc = dict()
        doc['id'] = str(comment['_id'])
        doc['parent'] = str(comment['p'])
        doc['user'] = comment['u']
        doc['comment'] = comment['t']
        dd = str(comment['c'])
        pos = dd.index('.')
        doc['date'] = dd[:pos]
        return doc
