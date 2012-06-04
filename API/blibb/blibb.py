# 
#
#	blibb.py
#
#

import logging
import json
from datetime import datetime
from bson.objectid import ObjectId
from bson import json_util
from API.base import BaseObject
from API.template.template import Template

class Blibb(BaseObject):

	@property
	def name(self):
		return self.__name

	@property
	def desc(self):
		return self.__desc

	@property
	def template(self):
		return self.__template

	@property
	def items(self):
		return self.__items

	@name.setter
	def name(self,value):
		self.__name = value

	@desc.setter
	def desc(self,value):
		self.__desc = value

	@template.setter
	def template(self,value):
		self.__template = value

	@items.setter
	def items(self,value):
		self.__items = value

	def __init__(self):
		super(Blibb,self).__init__('blibb','blibbs')
		self.__name = None
		self.__desc = None
		self.__items = []
		self.__template = None

	def populate(self):
		if self.doc is not None:
			self.name = self.doc.get('u')
			self.desc = self.doc.get('d')
			self.created = self.doc.get('c')
			self.id = self.doc.get('_id')
			self.items = self.doc.get('i')
			self.tags = self.doc.get('t')

	def save(self):
		self.objects.update(
				{u"_id" : ObjectId(self.id)},
				{"n" : self.name, "u": self.owner, "m": datetime.utcnow(), "i": self.items},
				True)



	def insert(self, user, name, slug, desc, template, image, group, invites):
		t = Template()
		t.load(template)
		now = datetime.utcnow()
		if group:
			gu = [user]
			doc = {"n" : name, "s": slug, "d": desc, "u": 'group', "gm": user, "gu": gu , "c": now, "nf": 0, "g": group, "t": t.dump(), "cc":0, "img" : image}
			# TODO send Email invites
		else:
			doc = {"n" : name, "s": slug, "d": desc, "u": user, "c": now, "nf": 0, "g": group, "t": t.dump(), "cc":0, "img" : image}

		newId = self.objects.insert(doc)
		d = dict()
		d['id'] = str(newId)
		return json.dumps(d)

	def getTemplate(self,obj_id):
		template =  self._objects.find_one({ u'_id': ObjectId(obj_id)}, {u't':1})
		return json.dumps(template,default=json_util.default)

	def incFollower(self,obj_id):
		self.objects.update({ u'_id': ObjectId(obj_id)}, {"$inc": {'nf': 1}}, True)
		return obj_id

	def howMany(self):
		return self.objects.count()

	def addToBlibbGroup(self, obj_id, user):
		self.objects.update({ u'_id': ObjectId(obj_id)}, {"$addToSet": {'gu': user}}, True)
		return obj_id
	
	def getByName(self,name):
		doc = self._objects.find_one({ u'n': name	})
		return json.dumps(doc,default=json_util.default)

	def describe(self):
		pass

	def getLabelFromTemplate(self, obj_id):
		result = self._objects.find_one({ u'_id': ObjectId(obj_id)}, {'t.i.n': 1, 't.i.s': 1})
		labels = dict()
		t = result['t']
		i = t['i']
		for r in i:
			labels[r['s']] = r['n']

		return labels
		 
	def getTemplateView(self, obj_id, view='Default'):
		res =  self.objects.find_one({ u'_id': ObjectId(obj_id)}, {'t.v': 1, 'n':1, 'd':1, 'c':1, 'u':1, 'tg':1, 's':1})
		buf = dict()
		if '_id' in res:
			t = res['t']
			v = t['v']
			buf[view] = v[view]
			buf['name'] = res['n']
			buf['description'] = res['d']
			buf['date'] = str(res['c'])
			buf['owner'] = res['u']
			buf['slug'] = res['s']
			if 'tg' in res:
				buf['tags'] = res['tg']
		else:
			buf['error'] = "view " + view + " does not exist"
		return json.dumps(buf,default=json_util.default)

	def getByIdParams(self, obj_id, params):
		p = dict()
		listparams = params.split(",")
		for param in listparams:
			p[param] = 1
		
		doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	}, p)
		return json.dumps(doc,default=json_util.default)

	def stripslashes(self,s):
		r = s.replace('\\n','')
		r = r.replace('\\t','')
		r = r.replace('\\','')
		return r

	def getByUser(self,username):
		r = self.objects.find({ u'u': username },{u't' : 0}).sort("c", -1)
		rs = []
		count = 0
		for result in r:
			buf = dict()		
			buf['name'] = result['n']
			buf['description'] = result['d']
			buf['id'] = str(result['_id'])
			buf['owner'] = result['u']
			buf['date'] = self.dateToString(result['c'])
			if 'img' in result:
				if 'thumbnails' in result['img']:
					buf['img_sizes'] = result['img'].get('thumbnails')
				if 'id' in result['img']:
					buf['img_id'] = result['img'].get('id')
			rs.append(buf)
			count += 1

		resp = dict()
		resp['count'] = count
		resp['results'] = rs
		return json.dumps(resp)


	def getBySlug(self,username, slug):
		
		r = self.objects.find({  u'u': username, u's': slug },{u't' : 0}).sort("c", -1)
		rs = []
		count = 0
		for result in r:
			buf = dict()		
			buf['name'] = result['n']
			buf['description'] = result['d']
			buf['id'] = str(result['_id'])
			buf['owner'] = result['u']
			buf['date'] = self.dateToString(result['c'])
			if 'img' in result:
				if 'thumbnails' in result['img']:
					buf['img_sizes'] = result['img'].get('thumbnails')
				if 'id' in result['img']:
					buf['img_id'] = result['img'].get('id')
			rs.append(buf)
			count += 1

		resp = dict()
		resp['count'] = count
		resp['results'] = rs
		return json.dumps(resp)

	def getIdBySlug(self,username, slug):
		r = self.objects.find_one({  u'u': username, u's': slug },{u'_id' : 1})
		oid = r.get('_id')
		res = dict()
		res['id'] = str(oid)
		return json.dumps(res)


	def getByGroupUser(self,username):
		result = self.objects.find({ u'gu': username },{u't' : 0}).sort("c", -1)
		return self.resultSetToJson(result)

