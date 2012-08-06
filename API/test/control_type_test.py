###
###
###     Control Type Unit Test
###
###
###
import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.control.control_type import ControlType


class ControlTypeTest(unittest.TestCase):

    def test_getControls(self):
        twitter = 61
        print ControlType.is_twitter(twitter)
        print ControlType.get_type(twitter)
