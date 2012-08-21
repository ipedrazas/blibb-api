###
###
###     surl Unit Test
###
###
###
import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.web.surl import SUrl


class TestTemplate(unittest.TestCase):

    def setUp(self):
        self.surl = SUrl()
        self.test_url = 'http://www.test.com'

    # def tearDown(self):
    #     self.remove(test_url)

    def test_add(self):
        print self.surl.add('http://blibb.net')
        print self.surl.add(self.test_url)

    def test_get(self):
        print self.surl.get('VEMf4')

