import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.om.manager import Manager
import logging
from API.blitem.blitem import Blitem
from datetime import datetime

class BlitemTest(unittest.TestCase):

	def test_getPageItems(self):
		b = Blitem()
		items = b.getItems({'u': 'ipedrazas', 'bs': 'names'}, {'i':1, 'tg': 1, 'b':1}, 2)

		for item in items:
			print item
		#owner, slug, tag, page=1

		# date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')




	# def test_save_parameters(self):
	# 	blitem = Blitem()
	# 	items = []
	# 	item = dict()
	# 	item['l'] = 'Label'
	# 	# ISODate("2005-06-01T13: 33: 00.0Z") 
	# 	item['v'] = datetime.strptime('21 5 2012', '%d %b %Y')
	# 	items = [item]

	# 	print blitem.insert('4fd0bc722ba78b765f00001a','test' 'UnitTest', items)


	def test_getAllItemsFlat(self):
		blitem = Blitem()
		a = blitem.getAllItemsFlat('4fd0bc722ba78b765f00001a')
		print a