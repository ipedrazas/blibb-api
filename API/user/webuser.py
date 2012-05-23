
from API.user.buser import User
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from API.event.event import Event
from API.control.bcontrol import BControl
import API.utils as utils

from flask import Blueprint, request, redirect, abort
import json


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
	e = Event('web.user.blibb.getBlibbBySlug')
	app_token = request.form['app_token']
	key = request.form['key']
	e.addLog({'at': app_token})
	e.addLog({'s': slug})

	tags = request.form['tags'] if 'tags' in request.form else ''
	user = utils.getKey(key)
	b = Blibb()
	jres =  b.getBySlug(username,slug)
	dres = json.loads(jres)
	results = dres.get('results')
	count = dres.get('count')
	if count == 1:
		jblibb = results[0]
		bid = jblibb['id']
		e.addLog({'b': bid})
		blitem = Blitem()
		labels = b.getLabelFromTemplate(bid)
		bitems = utils.getItemsFromRequest(labels, request)

	blitem_id = blitem.insert(bid, user, bitems, tags)
	e.save()
	return json.dumps(blitem_id) + "\n"


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