# 
#
#	event.py
#
#


from datetime import datetime
from API.base import BaseObject
import json
from bson import json_util
from pymongo import Connection
from bson.objectid import ObjectId

class Picture(BaseObject):

	def __init__(self):
		super(Picture,self).__init__('blibb','pictures')
		self.__owner = None
		self.__created = None
		self.__items = []
		self.__blibb = None

		
	def insert(self, blibb, owner, items):
		now = datetime.utcnow()
		doc = {"b" : blibb, "u": owner, "c": now, "i": items}
		newId = self.objects.insert(doc)
		return str(newId)

	def insertJson(self,jsonData):
		now = datetime.utcnow()
		data = json.loads(jsonData)
		newId = self.objects.insert(data)
		sId = dict()
		sId['id'] = str(newId)
		return json.dumps(sId)

	def updateJson(self,jsonData):
		data = json.loads(jsonData)
		pictId = data['id']
		del data['id']
		self.objects.update(
				{u"_id" : ObjectId(pictId)},
				data,
				False)
		sId = dict()
		sId['id'] = str(pictId)
		
		return json.dumps(sId)

	def getFlat(self, pict_id=None):
		if pict_id is None:
			return
		pict = self.objects.find_one({ u'_id': ObjectId(pict_id)})
		return json.dumps(pict,default=json_util.default)

	def dumpImage(self, pict_id=None):
		image = dict()
		if pict_id is None:
			return
		pictObj = self.objects.find_one({ u'_id': ObjectId(pict_id)})
		if pictObj is not None:
			image['id'] = pict_id
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


	def getImagesByUser(self,username):
		
		filter_dict = {'u': username}
		fields_dict = {'_id': 1}
		pictures = self.getImage(filter_dict, fields_dict)
		return pictures


	def getImage(self, filter_dict, fields_dict):
		res = self.objects.find(filter_dict, fields_dict)
		pictures = []
		for pict_id in res:
			pictures.append(str(pict_id.get('_id')))
		return pictures