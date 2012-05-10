

###
###
###		Utils Unit Test
###
###
###
import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
import API.utils as utils

class TestTemplate(unittest.TestCase):
	url = 'http://blibb.co/Ivan'
	print utils.getTitle(url)

