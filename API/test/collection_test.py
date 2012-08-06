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
from API.om.collection import Collection

import json


class TestCollection(unittest.TestCase):

    def test_get(self):
        print '########################   def test_get   #########################'
        c = Collection()
        list = c.get({'_id': ObjectId('500fffaf2ba78b05ba00001c')})
        print json.dumps(list)
        print '##################################################################'
        # print list

    def test_print_attr(self):
        print '########################   test_print_attr   ########################'
        c = Collection()
        print c.attr
        print '##################################################################'

    def test_list(self):
        print '#################  test_list   #############################'
        c = Collection()
        docs = c.list({'u': 'ipedrazas'}, {'n': 1}, num=5, page=4)
        print json.dumps(docs)
        print '##################################################################'

    def test_fork(self):
        print '#################  test_list   #############################'
        c = Collection()
        docs = c.fork('500fffaf2ba78b05ba00001c','manolete')
        print str(docs)
        print '##################################################################'
