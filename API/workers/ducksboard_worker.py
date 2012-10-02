#
#
#   worker ducksboard
#
#
import zmq
import time
import json
import requests
import sys
from os.path import join, abspath, dirname

parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.utils import get_config_value

KEY = get_config_value('DUCKSBOARD_KEY')

print "URL Worker running at port 5557"


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")


def set_value(value, endpoint):
    return send({'value': value}, endpoint)


def set_delta(endpoint):
    return send({'delta': 1}, endpoint)


def send(data, endpoint):
    req = requests.post("https://push.ducksboard.com/v/%s/" % endpoint,
                        auth=(KEY, 'ignored'),
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(data),
                        timeout=5)
    print req.status_code
    return req.content


def processMessage(message):
    strs = message.split('##')
    widget = strs[0]
    value = strs[1]
    action = strs[2]
    if action == 'd':
        set_delta(widget)
    elif action == 'v':
        set_value(value, widget)


while True:
    #  Wait for next request from client
    message = socket.recv()
    print "Received request: ", message
    print processMessage(message)
    #  Do some 'work'
    time.sleep(1)  # Do some 'work'
    socket.send('ok')
