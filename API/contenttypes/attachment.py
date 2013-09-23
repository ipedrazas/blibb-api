#
#
#   event.py
#
#

from datetime import datetime
from API.base import BaseObject
import json
from bson import json_util
from pymongo import Connection
from bson.objectid import ObjectId

from API.utils import get_config_value


conn = Connection(get_config_value('MONGO_URL'))
db = conn['blibb']
objects = db['attachments']


class Attachment(BaseObject):

    @classmethod
    def create(cls, owner, items={}, blibb_id=None):
        now = datetime.utcnow()
        doc = {"u": owner, "c": now, "i": items}
        if blibb_id:
            doc["b"] = blibb_id
        newId = objects.insert(doc)
        return str(newId)

    @classmethod
    def add_url(cls, attachment_id, url):
        objects.update({'_id': ObjectId(attachment_id)}, {'$set': {'l': url}})



    @classmethod
    def flat_(cls, attachment):
        dict_attach = dict()
        if attachment:
            if '_id' in attachment:
                dict_attach['id'] = str(attachment('_id'))
            if 'l' in image:
                dict_attach['url'] = attachment('l')
            if 'u' in image:
                dict_attach['owner'] = attachment('u')

        return dict_attach


