



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
from API.contenttypes.bookmark import Bookmark
from datetime import datetime
import json


class TestBookmark(unittest.TestCase):


	# def test_insert(self):
	# 	bk = Bookmark()
	# 	t = 'First Bookmark'
	# 	b = '4f952857f3a4181065000002'
	# 	bn = 'Test'
	# 	k = 'b1b00f4305a74818688b11f04bc6b869bf2fa42d'
	# 	user = 'ipedrazas'
	# 	url = 'http://www.blibb.net'
	# 	tags = []
	# 	tags.append('Dev')
	# 	tags.append('Test')

	# 	bk_id = bk.insert(b, user, url, t, bn, tags )
	# 	print bk_id

	def test_findByUrl(self):
		url ='https://github.com/buymeasoda/soda-theme'
		bk = Bookmark()
		bkid = bk.findByUrl(url) 
		print bk.id