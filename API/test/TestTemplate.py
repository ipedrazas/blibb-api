

###
###
###		Blitem Unit Test
###
###
###
import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.template.template import Template
import json
from datetime import datetime
import simplejson


class TestTemplate(unittest.TestCase):

	# def setUp(self):
	# 	pass
		
	# def test_insert(self):
	# 	now = datetime.utcnow()
	# 	b = Template()
	# 	b.name = 'my name' + str(now)
	# 	b.owner = 'ivan'
	# 	b.desc = 'This is a description'
		
	# 	nt = b.insert(b.name, b.desc, b.owner, 'draft')
	# 	b.addControl('1', nt, 'control', 'control', 1, 'my view', 'toto' )

	# def test_getByName(self):
	# 	b = Template()
	# 	# print b.getByName('my name')


	# def test_getControls(self):
	# 	t = Template()
	# 	ctrls = t.getTemplateControls('4f733922f3a4181945000000')

		# controls = list(cursor)
		# for elem in cursor:
		# 	controls = elem.get('ctrls')

		# for a in ctrls:
		# 	print a.get('c')
		# 	print a.get('t')
		# 	print a.get('v')

	def test_populate(self):
		t = Template()
		t.load('4f7f1350f3a41813f3000000')

		# print json.dumps(t,default=json_util.default)
		print t.dump()
		# ctrls = t.controls
		# for control in ctrls:
			# print control.get('s')

	# def test_wrapperEntry(self):
	# 	t = Template()
	# 	t.load('4f733922f3a4181945000000')
	# 	res = t.getWrapperEntry()
	# 	# print res

	# def test_cssEntry(self):
	# 	t = Template()
	# 	t.load('4f733922f3a4181945000000')
	# 	res = t.getCssEntry()
		# print res

	# def test_getHtmlWrapper(self):
	# 	t = Template()
	# 	t.load('4f733922f3a4181945000000')
	# 	res = t.getHtmlWrapper()
	# 	print 'test_getHtmlWrapper(self):'
	# 	print res
	
	# def test_CreateView(self):
	# 	t = Template()
	# 	t.load('4f7534bbf3a4180e58000000')
	# 	print t.createView('Default')
	
	# def test_getCssWrapper(self):
	# 	t = Template()
	# 	t.load('4f7534bbf3a4180e58000000')
	# 	print 'test_getCssWrapper(self):'
	# 	print t.getCssWrapper()

	# def test_publish(self):
	# 	t = Template()
	# 	t.load('4f7532caf3a4180dd3000000')
	# 	print 'test_publish(self):'
	# 	print t.publish()

	def test_getById(self):
		t = Template()
		tt =  simplejson.loads(t.getById('4f7ea549f3a4180981000007'))
		print tt
		
