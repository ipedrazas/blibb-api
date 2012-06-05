

from bs4 import BeautifulSoup
import urllib2
from flask import request
from API.control.bcontrol import BControl
from bson.objectid import ObjectId
import zmq
import redis
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


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



def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator