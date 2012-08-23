####
####
####
####
####
####

from datetime import datetime
from pymongo import Connection

from API.utils import get_config_value


conn = Connection(get_config_value('MONGO_URL'))
db = conn['blibb']
objects = db['management']


class Manager(object):

    @classmethod
    def validateCode(self, code=None):
        c = objects.find_one({'n': code, 'a': 1})
        if c:
            return True
        return False

    @classmethod
    def disableCode(self, code=None):
        objects.update({'n': code}, {"$set": {'a': 0}}, False)

    @classmethod
    def addCode(self, code=None, active=1):
        now = datetime.utcnow()
        c = objects.find_one({'n': code})
        if c:
            return "Code already exists in the system."
        doc = {"n": code, "a": active, "f": now, 'i': 0}
        newId = objects.insert(doc)
        return str(newId)

    @classmethod
    def addBetaUser(self, email, ip, browser):
        now = datetime.utcnow()
        doc = {"e": email, "i": ip, "c": now, 'b': browser}
        newId = objects.insert(doc)
        return str(newId)
