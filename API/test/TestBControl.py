

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
from API.control.bcontrol import BControl
from datetime import datetime
import json
from bson import json_util

class TestBControl(unittest.TestCase):

	# def setUp(self):
	# 	c = BControl()
	# 	c.name = 'Single Line Text Control'
	# 	c.owner = 'system'
	# 	c.ui = '<div id="{{c_id}}"><h3 class="click" data-tid="{{t_id}}" data-cid="{{c_id}}">Name</h3><b>Click Here to write your Field Name</b></div>'
	# 	views = dict()
	# 	views['default'] = '<label for="b-{{ctrl_slug}}">{{ctrl_name}}:</label><input name="b-{{ctrl_slug}}" placeholder="{{ctrl_name}}" size="50" type="text" />'
	# 	c.views = views
	# 	self.c = c
		
	# def test_save(self):
	# 	# self.c.save()
	# 	print ' >> New Object Created'

	# def test_getUiDefTemplate(self):
	# 	ui = self.c.getUiDefTemplate('4f69fd29ce794e1a1891e4e6')
	# 	print ui

	# # def test_getViewTemplate(self):
	# # 	view = self.c.getViewTemplate('4f6533c74059491db9e76e69')
	# # 	print 'VIEWS: ' + str(view)

	# def test_getAllControls(self):
	# 	print 'test_getAllControls'
	# 	c = BControl()
	# 	view = c.getAllControls()
	# 	print str(view)
	
	
	# def test_getIdNameList(self):
	# 	print 'test_getIdNameList'
	# 	c = BControl()
	# 	ctrls = json.loads(c.getIdNameList())
	# 	print ctrls
	# 	for c in ctrls.get('resultset'):
	# 		print c

	def test_constants(self):
		print BControl.TEXT

	def test_getType(self):
		print BControl.getType(BControl.MP3)

	def test_isMultitext(self):
		print 'Multitext: ' + str(BControl.MULTITEXT) + ' -' + BControl.getType(BControl.MULTITEXT) + ' - ' + str(BControl.isMultitext('02')) 

	def test_isMp3(self):
		print 'MP3: ' + str(BControl.MP3) + ' -' + BControl.getType(BControl.MP3) + ' - ' + str(BControl.isMp3('1f'))

	def test_isImage(self):
		print 'Image: ' + str(BControl.IMAGE) + ' -' + BControl.getType(BControl.IMAGE) + ' - ' + str(BControl.isImage('15'))

	def test_autoP(self):
		t = ''' 
				This is a sequence of
				stories 
				
				with a great charm
				vale
		'''
		print BControl.autoP(t)
