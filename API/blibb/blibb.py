# 
#
#	blibb.py
#
#

import logging
import json
from datetime import datetime

from bson.objectid import ObjectId
from pymongo import Connection

import API.utils as utils
from API.base import BaseObject
from API.template.template import Template
from API.contenttypes.picture import Picture
from API.error import Message




conn = Connection()
db = conn['blibb']
objects = db['blibbs']

class Blibb(object):

	def __init__(self):
		pass


	@classmethod
	def insert(self, user, name, slug, desc, template_id, image, read_access, write_access):
		t = Template()
		if utils.isValidId(template_id):
			t.load(template_id)
			now = datetime.utcnow()
			acl = dict()
			acl['read'] = read_access
			acl['write'] = write_access
			doc = {"n" : name, "s": slug, "d": desc, "u": user, "c": now,  "t": t.dump(), "img" : image, 'acl': acl}

			newId = objects.insert(doc)
			return str(newId)
		else:
			return Message.get('id_not_valid')

	def getTemplate(self,obj_id):
		if utils.isValidId(obj_id):
			template =  self._objects.find_one({ '_id': ObjectId(obj_id)}, {u't':1})
			return json.dumps(template,default=json_util.default)
		else:
			return Message.get('id_not_valid')


	def incFollower(self,obj_id):
		if utils.isValidId(obj_id):
			self.objects.update({ u'_id': ObjectId(obj_id)}, {"$inc": {'nf': 1}}, True)
			return obj_id

	def howMany(self):
		return self.objects.count()

	def addToBlibbGroup(self, obj_id, user):
		if utils.isValidId(obj_id):
			self.objects.update({ u'_id': ObjectId(obj_id)}, {"$addToSet": {'gu': user}}, True)
			return obj_id
	
	def getByName(self,name):
		doc = self._objects.find_one({ u'n': name	})
		return json.dumps(doc,default=json_util.default)

	@classmethod
	def getLabels(self, t):
		labels = dict()
		i = t['i']
		for r in i:
			labels[r['s']] = r['n']
		return labels

	@classmethod
	def getLabelFromTemplate(self, obj_id):
		labels = dict()
		if utils.isValidId(obj_id):
			result = objects.find_one({ '_id': ObjectId(obj_id)}, {'t.i.n': 1, 't.i.s': 1})					
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
	
	@classmethod 
	def getTemplateView(self, obj_id, view='Default'):
		if utils.isValidId(obj_id):
			res =  objects.find_one({ u'_id': ObjectId(obj_id)}, {'t.v': 1, 'n':1, 'd':1, 'c':1, 'u':1, 'tg':1, 's':1, 'img':1, 'ni':1, 'st.v':1})
			if '_id' in res:
				return self.flatObject(res)
			else:
				return "view " + view + " does not exist"

	@classmethod
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
			
			doc = self.getObject({ u'_id': ObjectId(obj_id)	}, p)
			return self.flatObject(doc)
		return Message.get('id_not_valid')

	def stripslashes(self,s):
		r = s.replace('\\n','')
		r = r.replace('\\t','')
		r = r.replace('\\','')
		return r

	def getBlibbs(self, filter, fields, page=1):
		PER_PAGE = 20
		docs = objects.find(filter,fields).sort("c", -1).skip(PER_PAGE * (page - 1)).limit(PER_PAGE )
		return docs

	def getByUser(self,username, page=1):
		r = self.getBlibbs({ 'u': username },{'t': 0}, page)
		rs = []
		count = 0
		for result in r:
			rs.append(self.flatObject(result))
			count += 1

		resp = dict()
		resp['count'] = count
		resp['results'] = rs
		return resp

	def getStats(self,doc):
		stats = []
		buf = dict()		
		if 'st' in doc:
			stts = doc.get('st')
			stats.append({'num_views': stts.get('v',0)})
			stats.append({'num_writes': stts.get('nw',0)})
			stats.append({'num_items': stts.get('ni',0)})

		return stats
			
	@classmethod
	def getIdBySlug(self,username, slug):
		r = objects.find_one({ 'u': username, 's': slug },{'_id' : 1})
		if r is not None:
			oid = r.get('_id', False)
			return str(oid)
		return False


	@classmethod
	def getFields(self, obj_id):
		if utils.isValidId(obj_id):
			doc = objects.find_one({ u'_id': ObjectId(obj_id)	}, {'t.i':1})
			template = doc.get('t').get('i')

			fields = []
			for elem in template:
				fields.append(elem.get('tx') + '-' + elem.get('s'))

			return fields

	@classmethod
	def getWebhooks(self, obj_id):
		if utils.isValidId(obj_id):
			doc = objects.find_one({ u'_id': ObjectId(obj_id)	}, {'wh':1})
			whs = doc.get('wh',[])
			# return template
			webhooks = []
			for wh in whs:
				w = {'action': wh.get('a'), 'callback': wh.get('u'), 'fields': wh.get('f')}
				webhooks.append(w)
			return webhooks

	@classmethod
	def incNumItem(self, condition):
		self.incView(condition, 'ni')
		self.incView(condition, 'nw')

	@classmethod
	def incView(self, condition, field):
		objects.update(condition, {"$inc": {'st.' + field: 1}})

	@classmethod
	def addTag(self, obj_id, tag):
		if utils.isValidId(obj_id):
			objects.update({ u'_id': ObjectId(obj_id)}, {"$addToSet": {'tg': tag.lower()}}, False)

	
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

	@classmethod
	def getObject(self, filter,fields):
		return objects.find_one(filter, fields)

	@classmethod
	def getBySlug(self,username, slug, page=1):		
		doc = self.getObject({  'u': username, 's': slug },{'t' : 0})
		return self.flatObject(doc)

	@classmethod
	def remove(self, filter):
		if filter is not None:
			objects.remove(filter)

