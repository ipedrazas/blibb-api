
from API.user.buser import User
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from API.event.event import Event
from flask import Blueprint, request, redirect, abort
import json

mod = Blueprint('user', __name__, url_prefix='')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is user'"


#####################
###### USERS  #######
#####################

@mod.route('/<username>/<slug>', methods=['GET'])
def getBlibbBySlug(username=None, slug=None):	

	'''
		
		Pass a blibb_id, get the blibb data
		get all the items, return a json doc with 
		blibb info and all the flat items

	'''
	e = Event('web.blibb.getBlibbBySlug')
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
		jitems = bl.getAllItemsFlat(bid)
		rs_items = json.loads(jitems)
		for i in rs_items:
			pass
		ret['items'] = rs_items['items']
	e.save()
	return json.dumps(ret)


@mod.route('/user/<user_id>', methods=['GET'])
def getUser(user_id=None):	
	e = Event('web.getUser')
	if user_id is None:
		abort(404)
	user = User()
	user.load(user_id)
	res = user.toJson()
	e.save()
	return res

@mod.route('/user/image', methods=['POST'])
def setImageUser():	
	e = Event('web.getUser')
	user_id = request.form['user_id']
	image_id = request.form['image_id']
	if user_id is None:
		abort(404)
	user = User()
	user.updateImageProfile(image_id)	
	e.save()
	return ''

@mod.route('/user/login', methods=['POST'])
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