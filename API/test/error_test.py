import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)


import unittest
from API.error import Message


class TestError(unittest.TestCase):

	def test_getErrors(self):		
		print Message.get('id_not_valid')