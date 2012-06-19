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
from bson import errors


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
			self.tags = self.doc.get('tg','')
			self.blibb = self.doc.get('b')

	def insert(self, blibb, user, items, tags=None):
		tag_list = []
		b = Blibb()
		try:
			b.load(blibb)
			b.populate()
			bs = b.slug
			if tags is not None:
				if ',' in tags:
					tag_list = list(set(tags.lower().split(',')))
				else:
					tag_list = list(set(tags.lower().split()))
				for t in tag_list:
					b.addTag(blibb,t)

			now = datetime.utcnow()
			doc = {"b" : ObjectId(blibb), "u": user, "bs": bs ,"c": now, "i": items, "cc": 0, 'tg': tag_list}
			newId = self.objects.insert(doc)
			return str(newId)
		except errors.InvalidId:
			return 'item_id is not valid'

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

	def flatObject(self, doc):
		blitem = dict()
		slugs = []
		if doc is not None:
			blitem_id = str(doc.get('_id',''))
			blitem['id'] = blitem_id
			blitem['parent'] = str(doc.get('b',''))
			blitem['num_comments'] = doc.get('cc','')
			i = doc.get('i',False)
			if i:
				for r in i:
					s = r.get('s', False)
					if s and s not in slugs:
						slugs.append(s)
					tt = dict()
					tt['value'] = r['v']
					tt['type'] = r['t']
					blitem[r['s']] = r['v']
				blitem['fields'] = slugs
			
			blitem['tags'] = doc.get('tg','')
			blitem['comments'] = self.getComments(blitem_id)
		return blitem


	def getFlat(self, obj_id):
		doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	})		
		item = self.flatObject(doc)
		return json.dumps(item)

	def getComments(self,obj_id):
		c = Comment()
		cs = c.getCommentsById(obj_id)
		return cs

	def getItemsPage(self, filter, fields, page=1):
		PER_PAGE = 20
		docs = self.objects.find(filter,fields).sort("c", -1).skip(PER_PAGE * (page - 1)).limit(PER_PAGE )
		return docs

	def getAllItemsFlat(self,blibb_id, page):
		docs = self.getItemsPage({u'b': ObjectId(blibb_id)},{'i':1, 'tg': 1}, page)
		result = dict()
		blitems = []
		for d in docs:
			blitems.append(self.flatObject(d))
		result['b_id'] = blibb_id
		result['count'] = len(blitems)
		result['items'] = blitems

		return json.dumps(result,default=json_util.default)


	def getItemsByTag(self, blibb_id, tag):
		docs = self.getItemsPage({'b': ObjectId(blibb_id), 'tg': tag}, {'i':1, 'tg': 1})
		result = dict()
		blitems = []
		
		for d in docs:
			blitems.append(self.flatObject(d))
			# blitems.append(blitem)

		result['count'] = len(blitems)
		result['items'] = blitems


		return result
	