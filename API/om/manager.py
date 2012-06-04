
from datetime import datetime
from API.base import BaseObject
from bson.objectid import ObjectId
import API.utils as utils


class Manager(BaseObject):

	def __init__(self):
		super(Manager,self).__init__('blibb','management')

	def validateCode(self, code=None):
		c = self.objects.find_one({'n': code, 'a': 1})
		if c:
			self.objects.update({ u'_id': c.get('_id')}, {"$inc": {'i': 1}}, False)
			self.debug('code validated')
			return True
		return False

	def disableCode(self, code= None):
		c = self.objects.update({ u'n': code}, {"$set": {'a': 0}}, False)	


	def listCodes(self):
		rs = self.objects.find()
		return self.resultSetToJson(rs)

	def addCode(self,code=None, active=1):
		now = datetime.utcnow()
		c = self.objects.find_one({'n': code})
		if c:
			raise Exception, "Code already exists in the system." 
		doc = {"n" : code, "a": active, "f": now, 'i': 0}
		newId = self.objects.insert(doc)
		return str(newId)