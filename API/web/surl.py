#
#
#   surl.py
#
#

from random import  sample
from string import digits, ascii_letters
from flask import current_app
from pymongo import Connection
from datetime import datetime

conn = Connection()
db = conn['blibb']
objects = db['urls']


class SUrl(object):

    @classmethod
    def short_id(cls, link):
        try:
            num = current_app.config.get('NUM_URL')
        except:
            num = 3
        url_id = "".join(sample(digits + ascii_letters, num))
        objects.insert({'u': url_id, 'l': link, 'h': 0, 'a': 0, 'c': datetime.utcnow()})
        return url_id

    @classmethod
    def get(cls, url_id=None):
        url = objects.find_one({'u': url_id})
        if url:
            objects.update({'_id': url['_id']}, {'$inc': {'h': 1}})
            return url['l']

    @classmethod
    def add(cls, link=None):
        url = objects.find_one({'l': link})
        if url:
            objects.update({'_id': url['_id']}, {'$inc': {'a': 1}})
            return url['u']
        else:
            return cls.short_id(link)

