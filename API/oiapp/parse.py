#
#
#
#

import httplib
import json
from API.utils import get_config_value
from flask import current_app


APPLICATION_ID = get_config_value('PARSE_APPLICATION_ID')
REST_API_KEY = get_config_value('PARSE_REST_API_KEY')


def do_push(name=None, channel=None, user=None):

    data = dict()

    data['data'] = {'alert': user + ': ' + name, 'badge': 'Increment', 'action': 'me.oioi.simple.OPENAPP', 'title': 'Oi!'}
    data["channels"] = [channel]

    head = dict()
    head['Content-Type'] = "application/json"
    head['X-Parse-Application-Id'] = APPLICATION_ID
    head['X-Parse-REST-API-Key'] = REST_API_KEY

    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('POST', '/1/push', json.dumps(data), head)

    current_app.logger.info(data)
    current_app.logger.info(head)
    resp = connection.getresponse().read()
    current_app.logger.info(resp)
    result = json.loads(resp)
    return result
