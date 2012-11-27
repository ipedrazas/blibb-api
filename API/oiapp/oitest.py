
import unittest
import requests
import json
import string
import random


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class TestOi(unittest.TestCase):


    def setUp(self):
        self.user = 'utest'
        self.pwd = 'utest'
        url = "http://api.blibb.net/users/login"
        req = requests.post(url, data={'username': self.user, 'password': self.pwd})
        json_res = req.content
        res = json.loads(json_res)
        self.key = res['key']
        self.oiid = self.create()



    def create(self):
        url = "http://api.blibb.net/ois"
        name = self.user + '-' + id_generator()
        req = requests.post(url, data={'login_key': self.key, 'name': name, 'contacts': 'utest2', 'tags': 'work'})
        json_res = req.content
        res = json.loads(json_res)
        oi = res['oi']
        if '_id' in oi:
            return str(oi['_id'])
        else:
            self.fail('object not created')

    def test_push(self):
        url = "http://api.blibb.net/ois/{0}/push".format(self.oiid)
        req = requests.post(url, data={'login_key': self.key})
        if req.status_code != 404:
            json_res = req.content
            res = json.loads(json_res)

    def test_not_push(self):
        url = "http://api.blibb.net/ois/{0}/push".format(self.oiid)
        req = requests.post(url, data={'login_key': '101'})
        # json_res = req.content
        if req.status_code != 401:
            self.fail('Should not be authorised to push')








