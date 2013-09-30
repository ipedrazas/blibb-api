#
#
#   event.py
#
#

from datetime import datetime
# from API.base import BaseObject
# import json
# from bson import json_util
from pymongo import Connection
from bson.objectid import ObjectId

from API.utils import get_config_value


conn = Connection(get_config_value('MONGO_URL'))
db = conn['blibb']
objects = db['pictures']


class Picture(object):

    # def __init__(self):
    #     super(Picture, self).__init__('blibb', 'pictures')
    #     self.__owner = None
    #     self.__created = None
    #     self.__items = []
    #     self.__blibb = None

    # def insert(self, blibb, owner, items):
    #     now = datetime.utcnow()
    #     doc = {"b": blibb, "u": owner, "c": now, "i": items}
    #     newId = self.objects.insert(doc)
    #     return str(newId)

    # def insertJson(self, jsonData):
    #     data = json.loads(jsonData)
    #     newId = self.objects.insert(data)
    #     sId = dict()
    #     sId['id'] = str(newId)
    #     return json.dumps(sId)

    # def updateJson(self, jsonData):
    #     data = json.loads(jsonData)
    #     pictId = data['id']
    #     del data['id']
    #     self.objects.update(
    #             {"_id": ObjectId(pictId)},
    #             data,
    #             False)
    #     sId = dict()
    #     sId['id'] = str(pictId)

    #     return json.dumps(sId)

    # def getFlat(self, pict_id=None):
    #     if pict_id is None:
    #         return
    #     pict = self.objects.find_one({'_id': ObjectId(pict_id)})
    #     return json.dumps(pict, default=json_util.default)

    @classmethod
    def create(cls, owner, items={}, blibb_id=None):
        now = datetime.utcnow()
        doc = {"u": owner, "c": now, "i": items}
        if blibb_id:
            doc["b"] = blibb_id
        newId = objects.insert(doc)
        return str(newId)

    @classmethod
    def add_url(cls, picture_id, url):
        objects.update({'_id': ObjectId(picture_id)}, {'$set': {'l': url}})

    @classmethod
    def dump_image(self, picture_id=None):
        image = dict()
        pictObj = objects.find_one({'_id': ObjectId(picture_id)})
        if pictObj is not None:
            image['id'] = picture_id
            pict = pictObj.get('i')
            image['format'] = pict.get('format')
            image['width'] = pict.get('width')
            image['height'] = pict.get('height')

            image['thumbnails'] = pict.get('thumb')
            image['file'] = pict.get('file')
            image['path'] = pict.get('path')

            image['mime_type'] = pict.get('mime_type')
            image['soft'] = pict.get('soft')
            image['size'] = pict.get('size')

        return image

    @classmethod
    def flat_image(cls, image):
        picture = dict()
        if image:
            if '_id' in image:
                picture['id'] = str(image('_id'))
            if 'l' in image:
                picture['url'] = image('l')
            if 'u' in image:
                picture['owner'] = image('u')

        return picture

    def getImagesByUser(self, username):
        filter_dict = {'u': username}
        fields_dict = {'_id': 1}
        pictures = self.getImage(filter_dict, fields_dict)
        return pictures

    @classmethod
    def get_images(self, filter_dict, fields_dict):
        res = objects.find(filter_dict, fields_dict)
        pictures = []
        for picture in res:
            pictures.append(self.dump_image())
        return pictures

    @classmethod
    def get_image_by_size(self, image, size):
        return image['path'] + size + '/' + image['id'] + '.' + image['format']
