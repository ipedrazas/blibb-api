# 
#
#	song.py
#
#


from datetime import datetime
from pymongo import Connection
from bson.objectid import ObjectId
from API.base import BaseObject
import json


class Song(BaseObject):

	def __init__(self):
		super(Song,self).__init__('blibb','songs')
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
		songId = data['id']
		self.objects.update(
				{u"_id" : ObjectId(songId)},
				data,
				False)
		sId = dict()
		sId['id'] = str(songId)
		items = data['i']
		del items['path']
		sId['song'] = items

		return json.dumps(sId)

	def dumpSong(self):
		s = dict()
		song = self.dump()
		if song is not None:
			s['id'] = song.get('_id')
			s['i'] = song.get('i')
		return s

	