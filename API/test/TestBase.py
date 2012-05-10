

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
from base import BaseObject
from blibb import Blibb
from blitem import Blitem
import json
from datetime import datetime

class TestBase(unittest.TestCase):

	def setUp(self):
		pass
		
	def test_slugigfy(self):
		text = 'Mi nombre es muy largo'
		b = BaseObject('blibb','base')
		a = b.slugify(text)
		print a

	def test_isOwner(self):
		b = Blibb()
		self.assertTrue(b.isOwner('4f86fe04711ee0394b000015','ipedrazas'))
		self.assertFalse(b.isOwner('4f86ffd1711ee0394b000038','ipedrazas'))
		bl = Blitem()
		self.assertTrue(bl.isOwner('4f86ffd1711ee0394b000038','ipedrazas'))
		self.assertFalse(bl.isOwner('4f86fe04711ee0394b000015','ipedrazas'))

