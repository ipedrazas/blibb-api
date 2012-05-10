

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
from API.contenttype.song import Song
from datetime import datetime
import json


class TestSong(unittest.TestCase):


	def test_dumpSong(self):
		s = Song()
		s.load('4f7aaf3f711ee00a4600000c')
		print s.dumpSong()
