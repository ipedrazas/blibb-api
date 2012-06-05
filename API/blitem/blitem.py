# 
#
#	blitem.py
#
#

import logging
import json
from datetime import datetime
from API.base import BaseObject
from API.blibb.blibb import Blibb
from API.comment.comment import Comment
from API.contenttypes.song import Song
from bson.objectid import ObjectId
from bson import json_util


class Blitem(BaseObject):

	@property
	def items(self):
		return self._items

	@property
	def blibb(self):
		return self._blibb

	@blibb.setter
	def blibb(self,value):
		self._blibb = value

	@items.setter
	def items(self,value):
		self._items = value

	def __init__(self):
		super(Blitem,self).__init__('blibb','blitems')
		self._blibb = None
		self._items = []



	def addItem(self, name, value):
		item = dict()
		item['l'] = name
		item['v'] = value
		self._items.append(item)
	
	def getItem(self,key):
		return self._items.get(key)

	def getKeys(self):
		return self._items.keys()

	def getValues(self):
		return self._items.values()

	def populate(self):
		if self.doc is not None:
			self.owner = self.doc.get('u')
			self.created = self.doc.get('c')
			self.id = self.doc.get('_id')
			self.items = self.doc.get('i')
			if 'tg' in self.doc:
				self.tags = self.doc.get('tg')
			self.blibb = self.doc.get('b')

	def insert(self, blibb, user, items, tags=None):
		tag_list = []
		if tags is not None:
			tag_list = list(set(tags.split()))
			# ToDO: this has to go through a queue
			b = Blibb()
			b.load(blibb)
			b.populate()
			bs = b.slug
			for t in tag_list:
				b.addTag(blibb,t)

		now = datetime.utcnow()
		doc = {"b" : ObjectId(blibb), "u": user, "bs": bs ,"c": now, "i": items, "cc": 0, 'tg': tag_list}
		newId = self.objects.insert(doc)
		return str(newId)

	def save(self):
		self.objects.update(
				{u"_id" : ObjectId(self.id)},
				{"$set": { "i": self.items}},
				True, False)

	def update(self, attr, value):
		self.objects.update(
				{u"_id" : ObjectId(self.id)}, {attr : value}
			)
		
		
	def getAllItems(self,blibb_id):
		docs = self.objects.find({u'b': ObjectId(blibb_id)},{'i':1}).sort("c", -1)
		return docs
		

	def getById(self,obj_id):
		doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	})
		return json.dumps(doc,default=json_util.default)

	def getRead(self,obj_id):
		doc = self.objects.find_one({ '_id': ObjectId(obj_id)},{'i':1})
		items = doc['i']
		return str(items['ri'])

	def getFlat(self, obj_id):
		doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	})
		blitem = dict()
		if doc is not None:
			iid = str(doc['_id'])
			blitem['id'] = iid
			blitem['b'] = str(doc['b'])
			blitem['cc'] = doc['cc']
			i = doc['i']
			for r in i:
				blitem[r['s']] = r['v']
			# pull the comments
			comments = self.getComments(iid)
			blitem['cs'] = comments

		return json.dumps(blitem,default=json_util.default)

	def getComments(self,obj_id):
		c = Comment()
		cs = c.getCommentsById(obj_id,True)
		return cs

	def getTagss(self,obj_id):
		c = Comment()
		cs = c.getCommentsById(obj_id,True)
		return cs

	def getAllItemsFlat(self,blibb_id):
		docs = self.objects.find({u'b': ObjectId(blibb_id)},{'i':1, 'tg': 1}).sort("c", -1)
		result = dict()
		blitems = []
		slugs = []
		types = []
		
		for d in docs:
			blitem = dict()
			iid = str(d['_id'])
			blitem['id'] = iid
			i = d['i']
			for r in i:
				if r['s'] not in slugs:
					slugs.append(r['s'])
				tt = dict()
				tt['v'] = r['v']
				tt['t'] = r['t']
				blitem[r['s']] = tt
			blitem['cs'] = self.getComments(iid)
			if 'tg' in d:
				blitem['tags'] = d['tg']

			blitems.append(blitem)

		result['b_id'] = blibb_id
		result['count'] = len(blitems)
		result['items'] = blitems
		result['fields'] = slugs

		return json.dumps(result,default=json_util.default)


	def getAllItemsFlat2(self,blibb_id):
		docs = self.objects.find({u'b': ObjectId(blibb_id)},{'i':1, 'tg': 1}).sort("c", -1)
		result = dict()
		blitems = []
		slugs = []
		types = []
		
		for d in docs:
			blitem = dict()
			iid = str(d['_id'])
			blitem['id'] = iid
			i = d['i']
			for r in i:
				if r['s'] not in slugs:
					slugs.append(r['s'])
				blitem[r['s']] = r['v']
			blitem['comments'] = self.getComments(iid)
			if 'tg' in d:
				blitem['tags'] = d['tg']

			blitems.append(blitem)

		result['b_id'] = blibb_id
		result['count'] = len(blitems)
		result['items'] = blitems
		result['fields'] = slugs

		return json.dumps(result,default=json_util.default)

	
		

