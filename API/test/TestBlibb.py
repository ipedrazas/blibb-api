

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
from blibb import Blibb
import json
from datetime import datetime
import re

class TestBlibb(unittest.TestCase):

	def setUp(self):
		pass
		
	def test_insert(self):
		now = datetime.utcnow()
		b = Blibb()
		b.name = 'my name' + str(now)
		b.owner = 'ivan'
		b.desc = 'This is a description'
		b.template = '4f7f129df3a41813b0000000'
		b.date = now
		print b.insert(b.owner, b.name, b.desc, b.template, False, '')

	# def test_getByName(self):
	# 	b = Blibb()
	# 	print b.getByName('my name')

	# def test_getById(self):
	# 	b = Blibb()
	# 	s = b.getById('4f756df7711ee00ad7000006')
	# 	print s

	# def test_getTemplate(self):
	# 	b = Blibb()
	# 	t = b.getTemplate('4f753e6df3a418112c000004')
		# print self.stripslashes(t)
		# print t.replace('','')

	def stripslashes(self,s):
		r = s.replace('\\n','')
		r = r.replace('\\t','')
		r = r.replace('\\','')
		return r

	# def test_getLabelsFromTemplate(self):
	# 	b = Blibb()
	# 	labels = b.getLabelFromTemplate('4f7613d0f3a4180c12000018')
	# 	print labels
	# 	print '###############'
	# 	print labels['titulolargo']
	# 	print labels.get('titulolargo')
		
	# def test_getTemplateView(self):
	# 	b = Blibb()
	# 	t = b.getTemplateView('4f7efbaef3a4180bad000000', 'Default')
		
	# 	print self.stripslashes(t)

	def test_getByIdParams(self):
		b = Blibb()
		
		params = 't.i.w,u'
		bi = b.getByIdParams('4f7efbaef3a4180bad000000',params)

		print self.stripslashes(bi)