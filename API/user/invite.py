



from datetime import datetime
from API.base import BaseObject
from bson.objectid import ObjectId


class Invite(BaseObject):

	def validate(self,code):
		doc = self.objects.find_one({'c': code, 's': 'active'})
		ret = dict()
		if doc is not None:
			ret['error'] = 0
			ret['msg'] = 'Code {1} is valid'

	def insert(self, code, status, description):
		doc = {"c" : code, "s": 'active', "d": description, "t": datetime.utcnow()}
		newId = self.objects.insert(doc)
		return str(newId)