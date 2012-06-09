import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.om.manager import Manager
import logging
from API.blitem.blitem import Blitem

class BlitemTest(unittest.TestCase):

	def test_getPageItems(self):
		b = Blitem()
		items = b.getItems({'u': 'ipedrazas', 'bs': 'names'}, {'i':1, 'tg': 1, 'b':1}, 2)

		for item in items:
			print item
		#owner, slug, tag, page=1