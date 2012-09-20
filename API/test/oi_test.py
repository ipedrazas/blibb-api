

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import unittest
from API.oiapp.models import User


class TestOi(unittest.TestCase):

    def test_create_user(self):

        user = User.create('ipedrazas@gmail.com', 'ivan', '0000100101')
        User.remove_role('ipedrazas@gmail.com', 'echo')
        # User.grant_role('ipedrazas@gmail.com', 'admin')
        # User.grant_role('ipedrazas@gmail.com', 'user')
        # User.grant_role('ipedrazas@gmail.com', 'spy')
        print user

