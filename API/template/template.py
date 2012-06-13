# 
#
#	template.py
#
#


from datetime import datetime
from API.base import BaseObject
from operator import itemgetter
from bson.objectid import ObjectId
from bson import json_util
import json

class Template(BaseObject):

	@property
	def name(self):
		return self.__name

	@property
	def desc(self):
		return self.__desc

	@property
	def date(self):
		return self.__date

	@property
	def author(self):
		return self.__author

	@property
	def views(self):
		return self.__views

	@property
	def controls(self):
		return self.__controls

	@controls.setter
	def controls(self,value):
		self.__controls = value

	@date.setter
	def date(self,value):
		self.__date = value

	@author.setter
	def author(self,value):
		self.__author = value

	@name.setter
	def name(self,value):
		self.__name = value

	@desc.setter
	def desc(self,value):
		self.__desc = value

	@views.setter
	def views(self,value):
		self.__views = value

	def __init__(self):
		super(Template,self).__init__('blibb','templates')
		self.__name = None
		self.__desc = None
		self.__author = None
		self.__views = []
		self.__controls = []

	def addControl(self, cid, tid, name, help, order, view, slug, typex):
		view = {'c': cid,  'n': name, 'h': help, 's': slug, 'o': order, 'w': view, 'tx': typex}
		self.objects.update({ u'_id': ObjectId(tid)}, {"$push": {'i': view}}, True)
		return cid


	def insert(self, name, desc, user, thumbnail, status):
		now = datetime.utcnow()
		doc = {"n" : name, "d": desc, "u": user, "c": now, "s": self.slugify(name), 't': thumbnail, 'q': status }
		newId = self.objects.insert(doc)
		return str(newId)

	def load(self, obj_id):
		self.__doc = self.objects.find_one({ '_id': ObjectId(obj_id)})
		self.populate()

	def toDict(self):
		r = dict()
		r['n'] = self.name
		r['d'] = self.desc
		r['c'] = self.created
		r['i'] = self.controls
		r['u'] = self.author

	def dump(self):
		return self.__doc
		
	def populate(self):
		if self.__doc is not None:
			self.name = self.__doc.get('n')
			self.created = self.__doc.get('c')
			self.id = self.__doc.get('_id')
			self.controls = self.__doc.get('i')
			self.author = self.__doc.get('u')


	def getTemplateControls(self, obj_id):
		controls = self.objects.find_one({ '_id': ObjectId(obj_id)},{'i':1})
		ctrls = controls.get('i')
		return sorted(ctrls, key=itemgetter('o')) 

	def getHtmlWrapper(self):
		res = '''
		<div class="{{slug}}Name">{{name}}<\/div>
		<div class="{{slug}}Desc">{{desc}}<\/div>
		<div class="{{slug}}Date">{{created}}<\/div>
		<div class="{{slug}}Author">{{owner}}<\/div>
		<div class="entryItems">{{#ENTRIES}}{{ENTRY}}{{\/ENTRIES}}<\/div>
				'''
		res = res.replace('{{ENTRY}}', self.getWrapperEntry())
		return res.replace('{{slug}}', self.slugify(self.name))

	def getCssWrapper(self):
		res = '''
		.{{slug}}Name{ font-size: 28px;background-color: black;color: white;font-weight: bolder;padding: 15px 35px;} 
		.{{slug}}Desc{ font-size:20px;padding: 15px 50px 20px 50px;background-color: gray;color: white;} 
		.{{slug}}Date{ display: none} 
		.{{slug}}Author{ display:none} 
		.entryItems{ margin-top: 20px;}
			'''
		return res.replace('{{slug}}', self.slugify(self.name))

	def getBlitemOptions(self):
		return '''<div id="options">
		<ul>
			<li><a href="#" name="comments" id="{{id}}">Comments<\/a><\/li>
			<li><a href="#" name="tags" id="{{id}}">Tags<\/a><\/li>
		<\/ul>
	</div>
'''

	def getControlsHtmlWrapper(self):
		pass
	
	def getControlWrite(self):
		pass

	def getControlRead(self, slug):
		return '<div class="' + slug + '">{{{' + slug + '}}</div>'


	def getControlCss(self, slug, style):
		if style is not None:
			return '.' + slug + ' { '+ style +'; }'
		else:
			return '.' + slug + ' {  }'

	def getWrapperEntry(self):
		res = '\n\t<div id="entry">\n\t\t'
		for control in self.controls:
			slug = control.get('s')
			ctype = control.get('t')
			if ctype == 'image':
				res += self.getControlReadImage(slug)
			elif ctype == 'song':
				res += self.getControlReadMusic(slug)
			else:
				res += self.getControlRead(slug)

			res += '\n\t\t'

		# res += self.getBlitemOptions()
		res += '</div><!-- div entry end -->' 
		return res

	def getControlReadMusic(self, slug):
		res = '<audio controls preload><source src="actions/playMp3?i={{'+ slug +'}}" /></audio>'
		return res

	def getControlReadImage(self, slug):
		return '<a href="actions/getImage?id={{' + slug + '}}&i=1" border="0"><img src="actions/getImage?id={{' + slug + '}}" alt="thumbnail" />'
	
	def getCssEntry(self):
		res = ''
		for control in self.controls:
			slug = control.get('s')
			css = control.get('l')
			res += self.getControlCss(slug, css)
			res += '\n'

		return res


	def createView(self, viewName, rb, sb, ri, si):		
		res = dict()
		res['rb'] =  rb
		res['sb'] = sb
		res['ri'] = ri
		res['si'] = si			
		self.objects.update({ u'_id': ObjectId(self.id)}, {"$push": {'v.' + viewName: res}, "$set": {'q':'active'}}, True)

	def createDefaultView(self):
		controls = self.getTemplateControls(self.id)
		rb = self.getHtmlWrapper()
		sb = self.getCssWrapper()
		ri = self.getWrapperEntry()
		si = self.getCssEntry()

		self.createView('Default', rb, sb, ri, si)
		

	def addView(self, obj_id, viewName, rb, sb, ri, si):
		# w rb sb ri si
		res = dict()
		res['rb'] =  rb
		res['sb'] = sb
		res['ri'] = ri
		res['si'] = si
			
		self.objects.update({ u'_id': ObjectId(obj_id)}, {"$push": {'v.' + viewName: res}}, True)


	def getById(self,obj_id):
		self.load(obj_id)
		return json.dumps(self.doc,default=json_util.default)


	def getActiveTemplates(self, status, params):
		p = dict()	
		listparams = params.split(",")
		for param in listparams:
			p[param] = 1

		result = self.objects.find({'q': status},p)		
		return self.resultSetToJson(result)

