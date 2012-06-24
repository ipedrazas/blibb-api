# 
#
#	blibb.py
#
#

import logging
import json
from datetime import datetime
from bson.objectid import ObjectId
import API.utils as utils
from API.base import BaseObject
from API.template.template import Template
from API.contenttypes.picture import Picture
from API.error import Message


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
		self.slug = None

	def populate(self):
		if self.doc is not None:
			self.name = self.doc.get('u')
			self.desc = self.doc.get('d')
			self.created = self.doc.get('c')
			self.id = self.doc.get('_id')
			self.items = self.doc.get('i')
			self.tags = self.doc.get('t')
			self.slug = self.doc.get('s')

	def save(self):
		if utils.isValidId(self.id):
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
		return str(newId)

	def getTemplate(self,obj_id):
		if utils.isValidId(obj_id):
			template =  self._objects.find_one({ '_id': ObjectId(obj_id)}, {u't':1})
			return json.dumps(template,default=json_util.default)
		else:
			return Message.get('id_not_valid')


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
		labels = dict()
		if utils.isValidId(obj_id):
			result = self._objects.find_one({ '_id': ObjectId(obj_id)}, {'t.i.n': 1, 't.i.s': 1})					
			if result is not None:
				t = result['t']
				i = t['i']
				for r in i:
					labels[r['s']] = r['n']
				return labels
			else:
				return {'count': 0}
		else:
			return {'error': 'Object id not valid'}
		 
	def getTemplateView(self, obj_id, view='Default'):
		res =  self.objects.find_one({ u'_id': ObjectId(obj_id)}, {'t.v': 1, 'n':1, 'd':1, 'c':1, 'u':1, 'tg':1, 's':1, 'img':1, 'ni':1, 'st.v':1})

		if '_id' in res:
			return self.flatObject(res)
		else:
			return {'error': "view " + view + " does not exist"}


	def flatObject(self, doc):
		buf = dict()
		
		buf['id'] = str(doc['_id'])
		if 't' in doc:
			buf['template'] = doc['t']
		if 'n' in doc:
			buf['name'] = doc['n']
		if 'd' in doc:
			buf['description'] = doc['d']
		if 'c' in doc:
			buf['date'] = str(doc['c'])
		if 'u' in doc:
			buf['owner'] = doc['u']
		if 's' in doc:
			buf['slug'] = doc['s']
		if 'ni' in doc:
			buf['num_items'] = doc.get('ni',0)
		if 'st' in doc:
			stats = doc.get('st')
			buf['num_views'] = stats.get('v',0)
		if 'img' in doc:
			img = doc['img']
			if 'id' in img:
				buf['img'] = img['id']
			else:
				buf['img'] = img
		if 'tg' in doc:
			buf['tags'] = doc['tg']

		return buf

	def getByIdParams(self, obj_id, params):
		p = dict()
		if utils.isValidId(obj_id):
			listparams = params.split(",")
			for param in listparams:
				p[param] = 1
			
			doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	}, p)
			return self.flatObject(doc)

		return Message.get('id_not_valid')
	def stripslashes(self,s):
		r = s.replace('\\n','')
		r = r.replace('\\t','')
		r = r.replace('\\','')
		return r

	def getBlibbs(self, filter, fields, page=1):
		PER_PAGE = 20
		docs = self.objects.find(filter,fields).sort("c", -1).skip(PER_PAGE * (page - 1)).limit(PER_PAGE )
		return docs

	def getByUser(self,username, page=1):
		r = self.getBlibbs({ 'u': username },{'t' : 0}, page)
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
		return resp


	def getBySlug(self,username, slug, page=1):		
		r = self.getBlibbs({  'u': username, 's': slug },{'t' : 0}, page)
		rs = []
		count = 0
		for result in r:
			buf = dict()		
			buf['name'] = result['n']
			buf['description'] = result.get('d','')
			buf['id'] = str(result['_id'])
			buf['owner'] = result['u']
			buf['tags'] = sorted(result.get('tg',''))
			buf['date'] = self.dateToString(result['c'])
			if 'img' in result:
				if 'thumbnails' in result['img']:
					buf['img_sizes'] = result['img'].get('thumbnails')
				if 'id' in result['img']:
					buf['img_id'] = result['img'].get('id')
			buf['stats'] = self.getStats(result)
			rs.append(buf)
			count += 1

		resp = dict()
		resp['count'] = count
		resp['results'] = rs
		return resp

	def getStats(self,doc):
		stats = []
		buf = dict()
		stats.append({'num_items': doc.get('ni',0)})
		if 'st' in doc:
			stts = doc.get('st')
			stats.append({'num_views': stts.get('v',0)})
			stats.append({'num_writes': stts.get('nw',0)})

		return stats
			

	def getIdBySlug(self,username, slug):
		r = self.objects.find_one({ 'u': username, 's': slug },{'_id' : 1})
		
		if r is not None:
			oid = r.get('_id', False)
			return str(oid)
		return False


	def getByGroupUser(self,username, page=1):
		result = self.getBlibbs({ 'gu': username },{'t' : 0}, page)
		return self.resultSetToJson(result)

	def getFields(self, obj_id):
		doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	}, {'t.i':1})
		template = doc.get('t').get('i')

		fields = []
		for elem in template:
			fields.append(elem.get('tx') + '-' + elem.get('s'))

		return fields

	def getWebhooks(self, obj_id):
		doc = self.objects.find_one({ u'_id': ObjectId(obj_id)	}, {'wh':1})
		whs = doc.get('wh',[])
		# return template
		webhooks = []
		for wh in whs:
			w = {'action': wh.get('a'), 'callback': wh.get('u'), 'fields': wh.get('f')}
			webhooks.append(w)
		return webhooks


	def incNumItem(self, condition):
		self.objects.update(condition, {"$inc": {'ni': 1}})

	def incView(self, condition, field):
		self.objects.update(condition, {"$inc": {'st.' + field: 1}})

	
	def addPicture(self, filter, picture_id):
		if utils.isValidId(picture_id):
			p = Picture()
			image = p.dumpImage(picture_id)
			self.objects.update(filter, {"$set": {'img': image}})
			return picture_id
		return Message.get('id_not_valid')

	def addComment(self, object_id, comment):
		pass

	def addWebhook(self, object_id, webhook):
		if utils.isValidId(object_id):
			self.objects.update({'_id': ObjectId(object_id)}, {'$pull': {'wh': {'a': webhook['a']}}})
			self.objects.update({'_id': ObjectId(object_id)},{'$addToSet':{'wh': webhook}})
		else:
			return Message.get('id_not_valid')