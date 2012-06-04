##
##
##	manager_test.py
##
##



import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.om.manager import Manager
import logging

class TestManager(unittest.TestCase):

	# def test_add_code(self):
	# 	logging.basicConfig(level=logging.WARNING)
	# 	log = logging.getLogger('example')
	# 	m = Manager()
	# 	m.setLog(logging.DEBUG)
	# 	try:
	# 		i = m.addCode('VOLL',1)
	# 		print i
	# 	except Exception, e:
	# 		log.error('Error from throws():')
	# 		# print e
		
	def test_list(self):
		m = Manager()
		print m.listCodes()

	def test_validate_code(self):
		code = 'TECHHUB'
		m = Manager()
		print m.getLogLevel()

		m.setLog(logging.DEBUG)
		if m.validateCode(code):
			print code + ' is a valid code '
		else:
			print 'Sorry, ' + code + ' code is not valid'
		code2 = 'INC2'
		if m.validateCode(code2):
			print code2 + ' is a valid code '
		else:
			print 'Sorry, ' + code2 + ' code is not valid'


	def test_disable_code(self):
		m = Manager()
		m.disableCode('DISABLED')