# 
#
#	event.py
#
#


from datetime import datetime
from pymongo import Connection
from API.base import BaseObject
from bson.objectid import ObjectId
import json


class Comment(BaseObject):

	def __init__(self):
		super(Comment,self).__init__('blibb','comments')
		self.__owner = None
		self.__created = None
		self.__parent = None
		self.__text = None
		self.__parentClass = None
		
	def insert(self, parent, owner, text, parentClass, thumbnail='/img/60x60.gif'):
		now = datetime.utcnow()
		doc = {"p" : parent, "u": owner, "c": now, "t": text, "pc": parentClass, 'th': thumbnail}
		newId = self.objects.insert(doc)
		return str(newId)

	def insertJson(self,jsonData):
		now = datetime.utcnow()
		data = json.loads(jsonData)
		newId = self.objects.insert(data)
		sId = dict()
		sId['id'] = str(newId)
		return json.dumps(sId)

	def getCommentsById(self, obj_id, asJson=False):
		docs = self.objects.find({ 'p': obj_id}).sort("c", -1)
		ddocs = []
		for d in docs:
			doc = dict()
			doc['id'] = str(d['_id'])
			doc['parent'] = d['p']
			doc['user'] = d['u']
			doc['comment'] = d['t']
			dd = str(d['c'])
			pos = dd.index('.')
			doc['date'] = dd[:pos]			 
			if 'ut' in doc:
				doc['user_image'] = d['ut']
			ddocs.append(doc)
		return ddocs

	
	