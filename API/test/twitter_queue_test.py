import zmq
import time


start_time = time.time()
print start_time
i = 0

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:5556")
socket.send (str(time.time()) + '##' + 'ipedrazas')
# socket.send (str(time.time()) + '##' + 'valgreens')
# socket.send (str(time.time()) + '##' + 'groove')
# socket.send (str(time.time()) + '##' + 'gallir')
# socket.send (str(time.time()) + '##' + 'jack')
# socket.send (str(time.time()) + '##' + 'rit')