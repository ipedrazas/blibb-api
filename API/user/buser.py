# 
#
#	User.py
#
#

from API.contenttypes.picture import Picture

from datetime import datetime
from API.base import BaseObject
from bson.objectid import ObjectId
import API.utils as utils
import json
import hashlib


class User(BaseObject):

	def __init__(self):
		super(User,self).__init__('blibb','users')
		self.__name = None
		self.__email = None
		self.__password = None
		self.__pub_salt = None
		self.__salt = None
		self.__active = False
		self.__created =  datetime.utcnow()
		self.__last_access = None
		self.__reset_code = None		
		self.__reg_code = None
		
	def save(self):
		user_id = self.objects.insert(
				{"n": self.name, "e" : self.email, "p": self.password, 
				"s": self.salt, "ps": self.pub_salt, "c" : self.created, 
				"a": self.active, 'l': self.last_access, 'rc': self.code,'rp': self.reset_code})
		return str(user_id)

	def toJson(self):
		u = dict()
		u['name'] = self.doc['n']
		u['id'] = str(self.doc['_id'])
		u['email'] = self.doc['e']
		if 'm' in self.doc:
			u['mini'] = self.doc['m']
		if 't' in self.doc:
			u['thumbnail'] = self.doc['t']

		return json.dumps(u)

	def authenticate(self, user, password):
		stUser = self.objects.find_one( {'$or': [{'e': user.strip()}, {'n':user.strip()}] })
		if stUser is not None:
			shPwd = hashlib.sha1(password + stUser['s'])
			print shPwd.hexdigest()
			print stUser['p']
			if stUser['p'] == shPwd.hexdigest():
				if 'i' in stUser:
					return self.setKey(str(stUser['_id']),stUser['n'],stUser['e'],stUser['i'])
				else:
					return self.setKey(str(stUser['_id']),stUser['n'],stUser['e'])
		return False


	def setKey(self,user_id, user_name, email, user_image=None):
		r = utils.getRedis()
		userkey = hashlib.sha1(user_name + user_id + str(datetime.utcnow())).hexdigest()
		r.set(userkey,user_name)
		basekey = userkey + ':'
		namekey = basekey + 'name'
		imagekey = basekey + 'thumbnail'
		emailkey = basekey + 'email'
		idkey = basekey + 'id'
		r.set(namekey,user_name)
		if user_image is None:
			image = '/img/60x60.gif'
		else:
			image = user_image.get('id')

		r.set(imagekey,image)
		r.set(idkey,user_id) 
		r.set(emailkey,email)
		expire = 3600
		r.expire(userkey,expire)
		r.expire(namekey,expire)
		r.expire(imagekey,expire)
		r.expire(emailkey,expire)
		r.expire(idkey,expire)

		return userkey


	def getByName(self,username):
		r = self.objects.find_one({ 'n': username },{ 'n': 1, 'e': 1, 'i': 1})
		res = dict()
		if r is not None:
			res['id'] = str(r.get('_id'))
			res['name'] = r.get('n')
			res['email'] = r.get('e')
			if 'i' in r:
				image = r.get('i')
				res['t60'] = '/actions/getImage?i=60&id=' + image.get('id')
				res['t160'] = '/actions/getImage?i=16&0id=' + image.get('id')
				res['t260'] = '/actions/getImage?i=260&id=' + image.get('id')
				res['image_id'] =  image.get('id')
		else:
			res['error'] = 'user not found'

		return res


	def addPicture(self, filter, picture_id):
		if picture_id is not None:
			p = Picture()
			image = p.dumpImage(picture_id)
			self.objects.update(filter, {"$set": {'i': image}}, True)
			return picture_id
		return 'error'


