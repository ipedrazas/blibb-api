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
import datetime
import pytz
from os.path import join, abspath, dirname

parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.oiapp.models import User, Oi
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


def set_timestamp_delta(endpoint):
    return send({"timestamp": time.time(), 'delta': 1}, endpoint)


def send(data, endpoint):
    req = requests.post("https://push.ducksboard.com/v/%s/" % endpoint,
                        auth=(KEY, 'ignored'),
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(data),
                        timeout=5)
    print req.status_code
    return req.content


def calculate_averages():
    total_num_ois = Oi.count()
    total_users = User.count()
    total_oi_user = total_num_ois / total_users
    set_value(total_oi_user, '81210')
    today = datetime.datetime.today().replace(tzinfo=pytz.utc)

    # ({'created_at':{'$gte': ISODate("2012-10-05T00:00:00.000Z")}}).count()
    num_ois_today = Oi.count({'created_at': {'$gte': today}})
    users_today = User.count({'created_at': {'$gte': today}})
    total_today = num_ois_today / users_today
    set_value(total_today, '81297')


def processMessage(message):
    strs = message.split('##')
    widget = strs[0]
    value = strs[1]
    action = strs[2]
    if action == 'd':
        set_delta(widget)
    elif action == 'v':
        set_value(value, widget)
    elif action == 'dt':
        set_timestamp_delta(widget)

averages_timeout = 1800
AVERAGE = 1800

while True:
    #  Wait for next request from client
    message = socket.recv()
    print "Received request: ", message
    print processMessage(message)
    if(averages_timeout > AVERAGE):
        calculate_averages()
        averages_timeout = 0
    #  Do some 'work'
    time.sleep(1)  # Do some 'work'
    socket.send('ok')
    averages_timeout += 1

