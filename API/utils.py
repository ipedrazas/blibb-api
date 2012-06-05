

from bs4 import BeautifulSoup
import urllib2
from flask import request
from API.control.bcontrol import BControl
from bson.objectid import ObjectId
import zmq
import redis


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


def getBlitemFromRequest(key, value, labels):
		slug = key[3:]
		typex = key[:2]
		blitem = {}
		blitem['t'] = typex
		blitem['s'] = slug
		if BControl.isMultitext(typex):
			value = BControl.autoP(value)
		elif BControl.isMp3(typex):
			song = Song()
			song.load(value)
			value = song.dumpSong()
		elif BControl.isImage(typex):
			value = ObjectId(value)	

		blitem['v'] = value
		blitem['l'] = labels.get(slug)
		return blitem

def getItemsFromRequest(labels, request):
	bitems = []
	for key,value in request.form.iteritems():
		if '-' in key:
			elem = getBlitemFromRequest(key, value, labels)
			bitems.append(elem)
	return bitems

def getKey(key):
	r = getRedis()
	return r.get(key)

def getRedis():
	return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

	