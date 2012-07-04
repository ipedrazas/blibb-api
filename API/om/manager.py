####
####
####
####
####
####

from datetime import datetime
from bson.objectid import ObjectId
import API.utils as utils
from pymongo import Connection

conn = Connection()
db = conn['blibb']
objects = db['blibbs']

class Manager(object):


	@classmethod
	def validateCode(self, code=None):
		c = objects.find_one({'n': code, 'a': 1})
		if c:
			return True
		return False

	@classmethod
	def useCode(self, code=None):
		objects.update({ u'_id': c.get('_id')}, {"$inc": {'i': 1}}, False)
		
	@classmethod
	def disableCode(self, code= None):
		c = objects.update({ u'n': code}, {"$set": {'a': 0}}, False)	

	@classmethod
	def addCode(self,code=None, active=1):
		now = datetime.utcnow()
		c = objects.find_one({'n': code})
		if c:
			raise Exception, "Code already exists in the system." 
		doc = {"n" : code, "a": active, "f": now, 'i': 0}
		newId = objects.insert(doc)
		return str(newId)

	@classmethod
	def addBetaUser(self, email, ip, browser):
		now = datetime.utcnow()
		doc = {"e" : email, "i": ip, "c": now, 'b': browser}
		newId = objects.insert(doc)
		return str(newId)