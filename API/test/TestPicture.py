###
###
###		Picture Unit Test
###
###
###
import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.contenttypes.picture import Picture
from datetime import datetime
import json

class TestPicture(unittest.TestCase):


	def test_getFlat(self):
		pict  = Picture()
		print pict.isValidId("4fa111812ba78b5854000001")
		image = pict.dumpImage("4fa111812ba78b5854000001")
		print image


	# def test_save(self):
	# 	pict = Picture()

		# items = dict()
		# items['size'] = 77068
		# items['format'] = 'png'
		# items['width'] = 1600
		# items['height'] = 900
		# items['mime_type'] = 'image\/png'
		# items['soft'] = 'gnome-screenshot'
		# items['file'] = '\/var\/www\/blibb.net\/php\/uploads\/ipedrazas\/images\/profile antonio.png'
	# 	print pict.insert('4f7ce34ef3a4180e1b00004d','ipedrazas',items)


	# def test_insertJson(self):

	# 	pict = Picture()
	# 	strJ = '{"i":{"size":116102,"format":"png","width":1600,"height":900,"mime_type":"image\/png","soft":"gnome-screenshot","file":"Screenshot at 2012-02-10 00:00:11.png","path":"\/var\/www\/blibb.net\/php\/uploads\/ipedrazas\/images\/Screenshot at 2012-02-10 00:00:11.png","t260":"\/var\/www\/blibb.net\/php\/uploads\/ipedrazas\/images\/260\/Screenshot at 2012-02-10 00:00:11.png"},"b":"4f7d7781f3a418241d000007","u":"ipedrazas"}'
	# 	# print pict.insertJson(strJ)

	# def test_updateJson(self):
	# 	pict = Picture()
	# 	strJ = '{"i":{"size":116102,"format":"png","width":1600,"height":900,"mime_type":"image\/png","soft":"gnome-screenshot","file":"Screenshot at 2012-02-10 00:00:11.png","path":"\/var\/www\/blibb.net\/php\/uploads\/ipedrazas\/images\/4f7dea52f3a4180aed000000.png","t260":"\/var\/www\/blibb.net\/php\/uploads\/ipedrazas\/images\/t260\/4f7dea52f3a4180aed000000.png"},"b":"4f7d7781f3a418241d000007","u":"ipedrazas","id":"4f7dea52f3a4180aed000000"}'
	# 	data = json.loads(strJ)
	# 	print data['id']
