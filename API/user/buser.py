# 
#
#	event.py
#
#


from datetime import datetime
from API.base import BaseObject
import json
import hashlib
import redis

class User(BaseObject):

	@property
	def name(self):
		return self.__name

	@property
	def email(self):
		return self.__email

	@property
	def pub_salt(self):
		return str(self.__pub_salt)

	@property
	def salt(self):
		return str(self.__salt)

	@property
	def password(self):
		return str(self.__password)

	@property
	def active(self):
		return self.__active

	@property
	def created(self):
		return self.__created

	@property
	def last_access(self):
		return self.__last_access

	@property
	def reset_code(self):
		return self.__reset_code

	@name.setter
	def name(self,value):
		self.__name = value

	@email.setter
	def email(self,value):
		self.__email = value
		self.__salt =  hashlib.sha1(value + str(datetime.utcnow())).hexdigest()
		self.__pub_salt = hashlib.sha1(value + str(datetime.utcnow())).hexdigest()

	@password.setter
	def password(self,value):
		self.__password = hashlib.sha1(value + self.salt).hexdigest()

	@active.setter
	def active(self,value):
		self.__active = value

	@last_access.setter
	def last_access(self,value):
		self.__last_access = value



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

		
	def save(self):
		user_id = self.objects.insert(
				{"n": self.name, "e" : self.email, "p": self.password, 
				"s": self.salt, "ps": self.pub_salt, "c" : self.created, 
				"a": self.active, 'l': self.last_access, 'rp': self.reset_code})
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
		stUser = self.objects.find_one( {'$or': [{'e': user}, {'n':user}] })
		if stUser is not None:
			shPwd = hashlib.sha1(password + stUser['s'])
			print shPwd.hexdigest()
			print stUser['p']
			if stUser['p'] == shPwd.hexdigest():
				if 'i' in stUser:
					return self.setKey(str(stUser['_id']),stUser['n'],stUser['i'])
				else:
					return self.setKey(str(stUser['_id']),stUser['n'])
		return False


	def setKey(self,user_id, user_name, user_image=None):
		r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
		userkey = hashlib.sha1(user_name + user_id + str(datetime.utcnow())).hexdigest()
		r.set(userkey,user_name)
		basekey = userkey + ':'
		namekey = basekey + 'name'
		imagekey = basekey + 'thumbnail'
		idkey = basekey + 'id'
		r.set(namekey,user_name)
		if user_image is None:
			user_image = '/img/60x60.gif'
		r.set(imagekey,user_image)
		r.set(idkey,user_id) 
		expire = 3600
		r.expire(userkey,expire)
		r.expire(namekey,expire)
		r.expire(imagekey,expire)
		r.expire(idkey,expire)

		return userkey
		

