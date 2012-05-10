

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
from datetime import datetime
import json
from API.blitem.blitem import Blitem
from API.control.bcontrol import BControl
from API.contenttypes.bookmark import Bookmark
import API.utils as utils


class TestBlitem(unittest.TestCase):

	# def setUp(self):
	# 	blitem = Blitem()
	# 	blitem.owner = 'UnitTest'
	# 	blitem.blibb = '12345'
	# 	blitem.date = datetime.utcnow()
	# 	item = dict()
	# 	item['l'] = 'Label'
	# 	item['v'] = 'Value'
	# 	blitem.items = [item]
	# 	blitem.addItem('Hello','Bye')
	# 	self.b = blitem
		
	# def test_save(self):
	# 	self.b.save()
	# 	print ' >> New Object Created'

	# def test_save_parameters(self):
	# 	blitem = Blitem()
	# 	items = []
	# 	item = dict()
	# 	item['l'] = 'Label'
	# 	item['v'] = 'Value'
	# 	items = [item]
	# 	print blitem.insert('345678', 'UnitTest', items)

	# def test_getAllItems(self):
	# 	blitem = Blitem()
	# 	docs = blitem.getAllItems('4f8173b0f3a418147e000005')
	# 	r = blitem.resultSetToJson(docs)
	# 	print r

	# def test_getAllItemsJson(self):
	# 	blitem = Blitem()
	# 	docs = blitem.getAllItemsFlat('4f7a6bbff3a4180963000008')
	# 	print docs

	# # def test_getById(self):
	# # 	blitem = Blitem()
	# # 	print '4f64babff3a41823fc000001 -- ' + blitem.getById('4f64babff3a41823fc000001')


	# def test_getFlat(self):
	# 	blitem = Blitem()
	# 	b = blitem.getFlat('4f7a6cc9f3a4180963000020')
	# 	print b

	def test_updateItems(self):
		blitem = Blitem()
		blitem.load('4f99146f2ba78b09b4000001')
		blitem.populate()
		items = blitem.items
		d = dict()
		d['l'] = 'http://docs.python.org/library/urlparse.html'
		d['d'] = "docs.python.org" 
		for item in items:
			if BControl.isURL(item['t']):
				item['v'] = d
		
		blitem.items = items
		blitem.save()

