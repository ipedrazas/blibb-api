


import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from event import Event

class TestEvent(unittest.TestCase):

	def setUp(self):
		self._e = Event('addBlibb')

	def test_addLog(self):
		self._e.addLog('My Event')
		L = []
		for i in range(100):
			L.append(i)
		self._e.save()

	def test_dates(self):
		e = Event('Test Dates')
		e.addLog('My Date Event')
		L = []
		for i in range(100):
			L.append(i)
		e.save(True)