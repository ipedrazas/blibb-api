
from API.user.buser import User
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from API.event.event import Event
from API.control.bcontrol import BControl
import API.blitem.weblitem as weblitem

from flask import Blueprint, request, redirect, abort
import json
import redis

mod = Blueprint('user', __name__, url_prefix='')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is user'"


#####################
###### USERS  #######
#####################

@mod.route('/<username>/<slug>', methods=['POST'])
def addItemtoBlibb(username=None, slug=None):

	if username is None:
		abort(404)
	if slug is None:
		abort(404)

	app_token = request.form['app_token']
	key = request.form['key']

	tags = request.form['tags'] if 'tags' in request.form else ''
	user = getKey(key)
	b = Blibb()
	jres =  b.getBySlug(username,slug)
	dres = json.loads(jres)
	results = dres.get('results')
	count = dres.get('count')
	if count == 1:
		jblibb = results[0]
		bid = jblibb['id']
		blitem = Blitem()
		labels = b.getLabelFromTemplate(bid)
		bitems = []
		for key,value in request.form.iteritems():
			if '-' in key:
				elem = getBlitemFromRequest(key, value, labels)
				bitems.append(elem)
	blitem_id = blitem.insert(bid, user, bitems, tags)

	return json.dumps(blitem_id) + "\n"


def getKey(key):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	return r.get(key)


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


@mod.route('/<username>/<slug>', methods=['GET'])
def getBlibbBySlug(username=None, slug=None):	
	'''
		
		Pass a blibb_id, get the blibb data
		get all the items, return a json doc with 
		blibb info and all the flat items

	'''
	e = Event('web.user.blibb.getBlibbBySlug')
	b = Blibb()
	if username is None:
		abort(404)
	if slug is None:
		abort(404)
	jres =  b.getBySlug(username,slug)
	dres = json.loads(jres)
	results = dres.get('results')
	count = dres.get('count')
	ret = dict()
	
	if count == 1:
		jblibb = results[0]
		bid = jblibb['id']
		ret['blibb'] = jblibb
		bl = Blitem()
		jitems = bl.getAllItemsFlat2(bid)
		rs_items = json.loads(jitems)
		for i in rs_items:
			pass
		ret['items'] = rs_items['items']
	e.save()
	return json.dumps(ret)


@mod.route('/user/name/<user_name>', methods=['GET'])
def getUserByName(user_name=None):	
	e = Event('web.user.getUserByName')
	if user_name is None:
		abort(404)
	user = User()
	u = user.getByName(user_name)
	res = json.dumps(u)
	e.save()
	return res

@mod.route('/user/<user_id>', methods=['GET'])
def getUser(user_id=None):	
	e = Event('web.user.getUser')
	if user_id is None:
		abort(404)
	user = User()
	user.load(user_id)
	res = user.toJson()
	e.save()
	return res

@mod.route('/user/image', methods=['POST'])
def setImageUser():	
	e = Event('web.user.setImageUser')
	user_id = request.form['user_id']
	image_id = request.form['image_id']
	if user_id is None:
		abort(404)
	user = User()
	user.addPicture(user_id, image_id)	
	e.save()
	return 'ok'


@mod.route('/login', methods=['POST'])
def doLogin():
	user = request.form['u']
	pwd = request.form['p']
	u = User()
	key = u.authenticate(user,pwd)
	if key:
		d = dict()
		d['key'] = key
		return json.dumps(d)
	else:
		abort(404)