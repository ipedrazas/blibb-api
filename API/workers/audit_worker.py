#
#
#   worker ducksboard
#
#
import zmq
import time

import sys
from os.path import join, abspath, dirname

parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)


print "URL Worker running at port 5558"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")


def processMessage(message):
    pass

while True:
    #  Wait for next request from client
    message = socket.recv()
    print "Received request: ", message
    print processMessage(message)
    #  Do some 'work'
    time.sleep(1)  # Do some 'work'
    socket.send('ok')
