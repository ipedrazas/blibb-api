

from bs4 import BeautifulSoup
import urllib2
from API.control.bcontrol import BControl
from bson.objectid import ObjectId
import zmq
import redis
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import re
from bson import errors


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
	value = value.strip()
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
	elif BControl.isDate(typex):
		# TODO: convert dates to MongoDates
		# and back
		value = value
	elif BControl.isTwitter(typex):
		value = re.sub('[!@#$]', '', value)

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

def postProcess(obj_id, items):
	for blitem in items:
		# print blitem
		typex = blitem['t']
		if BControl.isURL(typex):
			sendUrl(obj_id,blitem['v'])
		if BControl.isTwitter(typex):
			queueTwitterResolution(obj_id,blitem['v'])


def getKey(key):
	r = getRedis()
	return r.get(key)

def getRedis():
	return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)



def queueTwitterResolution(obj_id, twiter_screen_name):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect ("tcp://localhost:5556")
	if obj_id is not None:
		socket.send (str( obj_id + '##' + twiter_screen_name))

def isValidId(obj_id):
	try:
		oid = ObjectId(obj_id)
		return True
	except errors.InvalidId:
		return False
	except TypeError:
		return False
