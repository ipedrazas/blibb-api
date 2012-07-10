# 
#
#   BControl.py
#
#


from datetime import datetime
from bson.objectid import ObjectId
from pymongo import Connection
from API.user.buser import User


import logging
import sys
soh = logging.StreamHandler(sys.stdout)
soh.setLevel(logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(soh)


conn = Connection()
db = conn['blibb']
objects = db['bcontrols']


class Control(object):
    @classmethod
    def flat_object(self, doc):
        buf = dict()
        if doc:
            buf['id'] = str(doc['_id'])
        if 'n' in doc:
            buf['name'] = doc['n']
        if 'c' in doc:
            buf['date'] = str(doc['c'])
        if 'u' in doc:
            buf['owner'] = doc['u']
        if 'ui' in doc:
            buf['ui'] = doc['ui']
        if 'bt' in doc:
            buf['button'] = doc['bt']
        if 'tx' in doc:
            buf['type'] = doc['tx']
        if 'v' in doc:
            view = doc['v']
            buf['default'] = view.get('default')

        return buf

    @classmethod
    def get_all_controls(self):
        doc = objects.find({'u': 'system'})
        controls = []
        for ctrl in doc:
            controls.append(self.flat_object(ctrl))

        return controls

    @classmethod
    def insert(self, name, owner, ui, type, default, button):
        if User.is_admin(owner):
            logger.info('Is admin')
            now = datetime.utcnow()
            new_control = objects.insert({'n': name, 'c': now, 'u': 'system', 'tx': type})

            ui = self.replace_values(ui, str(new_control), name, type)
            default = self.replace_values(default, str(new_control), name, type)
            button = self.replace_values(button, str(new_control), name, type)

            d = {'default': default}

            objects.update({'_id': new_control}, {'$set': {'ui': ui, 'v': d, 'bt': button}})
            return str(new_control)
        logger.info('No admin')
        return False

    @classmethod
    def replace_values(self, attribute, id, name, type):
        attribute = attribute.replace('{{control_id}}', id)
        attribute = attribute.replace('{{control_name}}', name)
        attribute = attribute.replace('{{control_type}}', type)

        return attribute


class BControl(object):

    TEXT = 1
    MULTITEXT = 2
    DATE = 3
    LIST = 4
    IMAGE = 21
    MP3 = 31
    DOC = 41
    URL = 51
    TWITTER = 61

    def getUiDefTemplate(self, obj_id):
        doc = objects.find_one({'_id': ObjectId(obj_id)}, {'ui': 1})
        return doc['ui']

    def getViewTemplate(self, obj_id):
        doc = objects.find_one({'_id': ObjectId(obj_id)}, {'v.default': 1, 't': 1, 'tx': 1})
        res = dict()
        view = doc['v']
        res['v'] = view['default']

        tx = "0x%0.2x" % doc['tx']  # print hex number with leading 0
        res['tx'] = tx[2:]
        return res

    def save(self):
        objects.update(
                {u"_id": ObjectId(self.id)},
                {"n": self.name, "ui": self.ui, "u": self.owner, "tx": self.typex, "c": self.date, "v": self.views, "b": self.blibb, 'l': self.css},
                True)

    # def getIdNameList(self):
    #     docs = objects.find({'u': 'system'}, {'n': 1})
    #     return resultSetToJson(docs)

    @staticmethod
    def getType(typex):
        res = "0x%0.2x" % typex
        return res[2:]

    @staticmethod
    def isMultitext(typex):
        return typex == BControl.getType(BControl.MULTITEXT)

    @staticmethod
    def isMp3(typex):
        return typex == BControl.getType(BControl.MP3)

    @staticmethod
    def isImage(typex):
        return typex == BControl.getType(BControl.IMAGE)

    @staticmethod
    def isURL(typex):
        return typex == BControl.getType(BControl.URL)

    @staticmethod
    def isDate(typex):
        return typex == BControl.getType(BControl.DATE)

    @staticmethod
    def isTwitter(typex):
        return typex == BControl.getType(BControl.TWITTER)

    @staticmethod
    def autoP(text):
        res = ''
        buf = ''
        for line in text.split('\n'):
            line = line.strip()
            #if len(line) > 1:
            buf += line + '<br>'

        for line in buf.split('<br><br>'):
            line = line.strip()
            #if len(line) > 1:
            res += '<p>' + line + '</p>'

        res = res.replace('<br>', '\n')
        res = res.replace('<p></p>', '')
        res = res.replace('</p><p>', '</p>\n<p>')

        return res
