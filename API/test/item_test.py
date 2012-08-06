##
#
#
#

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from bson.objectid import ObjectId
from API.om.item import Item

import json


class TestItem(unittest.TestCase):

    def test_list(self):
        i = Item()
        list = i.get({'_id': ObjectId('500fffb32ba78b05ba00001f')})
        print json.dumps(list)
        # print list

    def test_print_attr(self):
        i = Item()
        print i.attr
