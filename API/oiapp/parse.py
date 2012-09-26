#
#
#
#

import urllib2
import json
from API.utils import get_config_value


API_ROOT = 'https://api.parse.com/1/'

APPLICATION_ID = get_config_value('PARSE_APPLICATION_ID')
REST_API_KEY = get_config_value('PARSE_REST_API_KEY')

PUSH_URL = API_ROOT + 'push'


def do_push(channel=None):

    data = dict()
    data['X-Parse-Application-Id'] = APPLICATION_ID
    data['X-Parse-REST-API-Key'] = REST_API_KEY
    data['data'] = 'Oi!'
    data['channels'] = [channel]

    request = urllib2.Request(PUSH_URL, json.dumps(data))
    response = urllib2.urlopen(request)
    response_body = response.read()
    response_dict = json.loads(response_body)
    return response_dict
