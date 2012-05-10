# 
#
#	BControl.py
#
#


import json
from datetime import datetime
from bson.objectid import ObjectId
from API.base import BaseObject


class BControl(BaseObject):

	TEXT = 1
	MULTITEXT = 2
	DATE = 3
	LIST = 4
	IMAGE = 21
	MP3 = 31
	DOC = 41
	URL = 51


	def __init__(self):
		super(BControl,self).__init__('blibb','bcontrols')
		self.__ui = None
		self.__views = dict()
		self.__name = None
		self.__blibb = None
		self.__css = None
		self.__typex = None

	@property
	def name(self):
		return self.__name

	@property
	def typex(self):
		return self.__typex

	@property
	def css(self):
		return self.__css

	@property
	def blibb(self):
		return self.__blibb

	@property
	def ui(self):
		return self.__ui

	@property
	def views(self):
		return self.__views

	@blibb.setter
	def blibb(self,value):
		self.__blibb = value

	@typex.setter
	def typex(self,value):
		self.__typex = value

	@css.setter
	def css(self,value):
		self.__css = value

	@name.setter
	def name(self,value):
		self.__name = value

	@ui.setter
	def ui(self,value):
		self.__ui = value

	@views.setter
	def views(self,value):
		self.__views = value


	def save(self, user, name, desc, template, group, invites):
		pass

	def populate(self):
		if self.doc is not None:
			self.ui= self.doc.get('ui')
			self.css = self.doc.get('l')

	def getUiDefTemplate(self,obj_id):
		doc = self.objects.find_one({ '_id': ObjectId(obj_id)},{'ui':1})
		return doc['ui']

	def getViewTemplate(self,obj_id):
		doc = self.objects.find_one({ '_id': ObjectId(obj_id)},{'v.default':1,'t':1, 'tx':1})
		res = dict()
		view =  doc['v']
		res['v'] = view['default']
		
		tx = "0x%0.2x" % doc['tx'] # print hex number with leading 0
		res['tx'] = tx[2:]
		return res

	def save(self):
		self.objects.update(
				{u"_id" : ObjectId(self.id)},
				{"n": self.name, "ui" : self.ui, "u": self.owner, "tx": self.typex, "c": self.date, "v" : self.views, "b": self.blibb, 'l': self.css},
				True)


	def getAllControls(self):
		controls = self.objects.find({ 'u': 'system'})
		return self.resultSetToJson(controls)

	def getIdNameList(self):
		docs = self.objects.find({ 'u': 'system'},{'n':1})
		return self.resultSetToJson(docs)

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
	def autoP(text):
		res = ''
		buf = ''
		for line in text.split('\n'):
			line = line.strip()
			#if len(line) > 1:
			buf +=  line + '<br>'

		for line in buf.split('<br><br>'):
			line = line.strip()
			#if len(line) > 1:
			res +=  '<p>' +  line + '</p>'

		res = res.replace('<br>','\n')
		res = res.replace('<p></p>', '')
		res = res.replace('</p><p>', '</p>\n<p>')

		return res

