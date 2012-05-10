# 
#
#	event.py
#
#

import json
from urlparse import urlparse
from datetime import datetime

from pymongo import Connection
from bson.objectid import ObjectId
from bson import json_util

from API.base import BaseObject




class Bookmark(BaseObject):

	@property
	def url(self):
		return self._url

	@property
	def title(self):
		return self._title

	@property
	def domain(self):
		return self._domain

	@property
	def blibb(self):
		return self._blibb

	@property
	def saves(self):
		return self._saves

	@saves.setter
	def saves(self,value):
		self._saves = value

	@blibb.setter
	def blibb(self,value):
		self._blibb = value

	@url.setter
	def url(self,value):
		self._url = value

	@title.setter
	def title(self,value):
		self._title = value

	@domain.setter
	def domain(self,value):
		self._domain = value

	def __init__(self):
		super(Bookmark,self).__init__('blibb','bookmarks')
		self._origin = None
		self._url = None
		self._title = None
		self._blibb = []
		self._domain = None
		self._saves = 0
		self._users = []

	def save(self):
		now = datetime.utcnow()
		domain = urlparse(self.url)
		if self.saves == 0:
			self.saves = 1
		doc = {"b" : ObjectId(self.blibb), "u": self.owner, "c": now, "l": self.url, 't': self.title, "d": domain.netloc , 'tg': self.tags, 'bn': self.bn, 's': self.saves}
		newId = self.objects.insert(doc)
		self.id = newId 

	
	def createByUrl(self, url, owner):
		now = datetime.utcnow()
		doc = {"u": owner, "c": now, "l": url}
		newId = self.objects.insert(doc)
		return str(newId)

	def insert(self, blibb, owner, url, title, tags):
		now = datetime.utcnow()
		domain = urlparse(url)
		users = []
		users.append(owner)
		blibbs = []
		blibbs.append(ObjectId(blibb))
		doc = {"b" : blibbs, "u": users, "c": now, "l": url, 't': title, "d": domain.netloc , 'tg': tags, 's': 1}
		self.debug(doc)
		newId = self.objects.insert(doc)
		return str(newId)

	def populate(self):
		if self.doc is not None:
			self.url = self.doc.get('l')
			self.title = self.doc.get('t')
			self.id = self.doc.get('_id')
			self.domain = self.doc.get('d')
			self.users = self.doc.get('u')
			self.tags = self.doc.get('tg')
			self.saves = self.doc.get('s')

	def init(self, doc):
		self.url = doc.get('l')
		self.title = doc.get('t')
		self.id = doc.get('_id')
		self.domain = doc.get('d')
		self.users = doc.get('u')
		if 'tg' in doc:
			self.tags = doc.get('tg')
		self.saves = doc.get('s')

	def findByUrl(self,url):
		self.doc = self.objects.find_one({ 'l': url })
		return self.id
		

	def dumpBookmark(self):
		s = dict()
		bk = self.dump()
		if bk is not None:
			s['id'] = bk.get('_id')
			s['url'] = bk.get('l')
			s['domain'] = bk.get('d')
			s['saved'] = bk.get('s')
			s['title'] = bk.get('t')
		return s

	def add(self, blibb, owner, tags):
		for tag in tags:
			self.objects.update({ u'_id': ObjectId(self.id)}, {"$addToSet": {'tg': tag}}, False, False)
		self.objects.update({ u'_id': ObjectId(self.id)}, {"$addToSet": {'u': owner}}, False, False)
		self.objects.update({ u'_id': ObjectId(self.id)}, {"$addToSet": {'b': ObjectId(blibb)}}, False, False)
		self.objects.update({ u'_id': ObjectId(self.id)}, {"$inc": {'s': 1}}, False, False)

	

