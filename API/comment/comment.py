# 
#
#	event.py
#
#


from datetime import datetime
from pymongo import Connection
from API.base import BaseObject
from bson.objectid import ObjectId
from bson import errors
import json

class Comment(BaseObject):

	def __init__(self):
		super(Comment,self).__init__('blibb','comments')
		self.__owner = None
		self.__created = None
		self.__parent = None
		self.__text = None
		self.__parentClass = None
		
	def insert(self, parent, owner, text):
		now = datetime.utcnow()
		try:
			doc = {"p" : ObjectId(parent), "u": owner, "c": now, "t": text}
			newId = self.objects.insert(doc)
			return str(newId)

		except errors.InvalidId:
			return 'item_id is not valid'

	def insertJson(self,jsonData):
		now = datetime.utcnow()
		data = json.loads(jsonData)
		newId = self.objects.insert(data)
		sId = dict()
		sId['id'] = str(newId)
		return json.dumps(sId)

	def getCommentsById(self, obj_id, asJson=False):
		docs = self.objects.find({ 'p': ObjectId(obj_id)}).sort("c", -1)
		ddocs = []
		for d in docs:
			ddocs.append(self.flatObject(d))
		return ddocs


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



	def getCommentFlat(self, obj_id):
		try:
			doc = self.objects.find_one({ '_id': ObjectId(obj_id)	})			
			return self.flatObject(doc)
		except errors.InvalidId:
			return 'item_id is not valid'

	
	