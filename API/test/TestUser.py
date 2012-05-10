

###
###
###		User Unit Test
###
###
###

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)


import unittest
from API.user.buser import User


class TestUser(unittest.TestCase):

	# def test_save(self):
	# 	user = User()
	# 	user.name = 'Ivan'
	# 	user.email = 'ivan@blibb.net'
	# 	user.password = 'ivan'
	# 	user.active = True

	# 	uid = user.save()
	# 	print uid

	def test_Authenticte(self):
		u = User()
		print u.autheticate('ipedrazas','ivan')