

import zmq


class UrlWorker(object):

	def __init__(self):
		self.__context = zmq.Context()
		self.__socket = self.__context.socket(zmq.REQ)
		self.__socket.connect ("tcp://localhost:5555")

	def send(self,url, obj_id):
		if obj_id is not None:
			socket.send (obj_id + '##' + url)

