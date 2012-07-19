import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from bson.objectid import ObjectId

from API.control.control_type import ControlType
from API.blitem.blitem import Blitem


class BlitemTest(unittest.TestCase):

    # def test_getPageItems(self):
    #     b = Blitem()
    #     items = b.getItems({'u': 'ipedrazas', 'bs': 'names'}, {'i': 1, 'tg': 1, 'b': 1}, 2)

    #     for item in items:
    #         print item
        #owner, slug, tag, page=1

        # date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')

    # def test_save_parameters(self):
    #   blitem = Blitem()
    #   items = []
    #   item = dict()
    #   item['l'] = 'Label'
    #   # ISODate("2005-06-01T13: 33: 00.0Z")
    #   item['v'] = datetime.strptime('21 5 2012', '%d %b %Y')
    #   items = [item]

    #   print blitem.insert('4fd0bc722ba78b765f00001a','test' 'UnitTest', items)

    # def test_getAllItemsFlat(self):
    #     blitem = Blitem()
    #     a = blitem.getAllItemsFlat('4fd0bc722ba78b765f00001a')
    #     print a

    # def test_get_item(self):
    #     i_id = '5007ddd42ba78b3b4c000006'
    #     b = Blitem.get_item({'_id': ObjectId(i_id)})
    #     print str(b)

    def test_get_flat(self):
        i_id = '4fdb17452ba78b162f00002b'
        b = Blitem.get_flat(i_id)
        print str(b)

    # def test_update_ite(self):
    #     i_id = '5007ddd42ba78b3b4c000006'
    #     b = Blitem.get_item({'_id': ObjectId(i_id)})
    #     items = b['i']
    #     for item in items:
    #         type = item['t']
    #         if ControlType.is_twitter(type):
    #             item['v'] = 'Pachuli'
    #     Blitem.update_from_dict(b)
