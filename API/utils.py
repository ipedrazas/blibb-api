

from bs4 import BeautifulSoup
import urllib2

import zmq


def getTitle(url):
		page = urllib2.urlopen(url)
		soup = BeautifulSoup(page)
		if hasattr(soup, 'head') and hasattr(soup,'title'):
			return soup.head.title.string.encode('utf-8')

		return ''


def sendUrl(obj_id, url):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect ("tcp://localhost:5555")
	if obj_id is not None:
		socket.send (str(obj_id + '##' + url))

	