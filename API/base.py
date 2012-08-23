#
#
#   blitem.py
#
#

import json
import re
from unicodedata import normalize
from datetime import datetime

from API.utils import get_config_value
from pymongo import Connection
from bson.objectid import ObjectId
from bson import json_util


class BaseObject(object):

    @property
    def id(self):
        return self._id

    @property
    def url(self):
        return self._url

    @property
    def doc(self):
        return self._doc

    @property
    def owner(self):
        return self._owner

    @property
    def date(self):
        return self._created

    @property
    def logger(self):
        return self._logger

    @property
    def objects(self):
        return self._objects

    @property
    def tags(self):
        return self._tags

    @id.setter
    def id(self, value):
        self._id = value

    @url.setter
    def url(self, value):
        self._url = url

    @owner.setter
    def owner(self, value):
        self._owner = value

    @doc.setter
    def doc(self, value):
        self._doc = value

    @date.setter
    def date(self, value):
        self._created = value

    @tags.setter
    def tags(self, value):
        self._tags = value

    def __init__(self, db, collection):
        self._db = db
        self._collection = collection
        self._conn = Connection(get_config_value('MONGO_URL'))
        self._db = self._conn[self._db]
        self._objects = self._db[self._collection]
        self._id = None
        self._owner = None
        self._created = datetime.utcnow()
        self._tags = []
        self._doc = None
        self._cursor = None


    def slugify(self, text, delim=u''):
        """Generates an slightly worse ASCII-only slug."""
        _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?:@\[\\\]^_`{|},.]+')
        result = []
        for word in _punct_re.split(text.lower()):
            word = normalize('NFKD', unicode(word)).encode('ascii', 'ignore')
            if word is not None:
                result.append(word)

        return unicode(delim.join(result))

    def load(self, obj_id):
        self._doc = self._objects.find_one({'_id': ObjectId(obj_id)})

    def __populate(self):
        pass

    def getById(self, obj_id):
        self.load(obj_id)
        return json.dumps(self._doc, default=json_util.default)

    def toJson(self, doc):
        return json.dumps(doc, default=json_util.default)

    def addTag(self, obj_id, tag):
        # don't need to check if tags exists for duplicates. Only stores one
        # case unsensitive FTW!
        self._objects.update({u'_id': ObjectId(obj_id)}, {"$addToSet": {'tg': tag.lower()}}, False)

    def resultSetToJson(self, resultSet):
        rs = []
        res = dict()
        res['count'] = resultSet.count()
        for p in resultSet:
            rs.append(json.dumps(p, default=json_util.default))

        res['resultset'] = rs
        return json.dumps(res)

    def dump(self):
        return self._doc

    def cleanUp(self, text):
        text = text.replace("\\", "")
        text = text.replace("\"{", "{")
        text = text.replace("}\"", "}")
        return text

    def isOwner(self, obj_id, person):
        res = self._objects.find_one({u'_id': ObjectId(obj_id), 'u': person})
        if res:
            return True
        else:
            return False

    def incCommentsCounter(self, obj_id):
        self._objects.update({u'_id': ObjectId(obj_id)}, {"$inc": {'cc': 1}})

    def dateToString(self, date):
        return date.strftime("%a, %d %b %Y %H:%M:%S ")

    def remove(self, filter):
        if filter is not None:
            self._objects.remove(filter)

    def getObjects(self, filter_dict, fields_dict):
        res = self.objects.find(filter_dict, fields_dict)
        objects = []
        for o in res:
            row = dict()
            for field in fields_dict:
                row[field] = o.get(field)
            objects.append(row)
        return objects
