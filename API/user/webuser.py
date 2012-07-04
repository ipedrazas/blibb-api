#
#
#
#
#
#
#


from API.om.manager import Manager
from API.user.buser import User
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from API.event.event import Event
from API.control.bcontrol import BControl
import API.utils as utils
from bson.objectid import ObjectId
from flask import Blueprint, request, redirect, abort, current_app, jsonify
from functools import wraps
import json
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.decorators import cached
from API.error import Message


mod = Blueprint('user', __name__, url_prefix='')

ANON_APPS = {
	'QPGQ': 'quidprogquo',
	'QUOTR': 'quotr',
	'test': 'test'
}

@mod.route('/favicon.ico')
@mod.route('/robots.txt')
@mod.route('/index.html')
@mod.route('/scripts/<path:any>')
def handle(any=None):
    abort(404)

@mod.route('/hi')
def hello_world():
	return "Hello World, this is user'"

#####################
###### USERS  #######
#####################

@mod.route('/<username>/<slug>/action/delete', methods=['POST'])
@crossdomain(origin='*')
def deleteBlibb(username=None, slug=None):
	e = Event('web.user.blibb.deleteItem')
	if username is None:
		abort(404)
	if slug is None:
		abort(404)
	b = Blibb()
	dres =  b.getBySlug(username,slug)
	results = dres.get('results','')
	count = dres.get('count',0)
	if count > 0:
		jblibb = results[0]
		bid = jblibb['id']
		filter = { '_id': ObjectId(bid)}
		b.remove(filter)

	e.save()

@mod.route('/<username>/<slug>/del/<item_id>', methods=['POST'])
@crossdomain(origin='*')
def deleteItem(username=None, slug=None, item_id=None):
	e = Event('web.user.blibb.deleteItem')
	if username is None:
		abort(404)
	if slug is None:
		abort(404)
	if item_id is None:
		abort(404)

	e.save()

@mod.route('/<username>/<slug>', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def addItemtoBlibb(username=None, slug=None):
	e = Event('web.user.blibb.getBlibbBySlug')
	if username is None:
		abort(404)
	if slug is None:
		abort(404)	
	app_token = request.form['app_token']
	key = request.form['key']
	e.addLog({'at': app_token})
	e.addLog({'s': slug})

	tags = request.form['tags'] if 'tags' in request.form else ''
	user = isAnonApp(key)
	if not user:
		user = utils.getKey(key)
		
	blibb =  Blibb.get_by_slug(username,slug)
	if blibb:
		owner = blibb.get('u','')
		if owner == user:
			bid = blibb['id']
			e.addLog({'b': bid})
			blitem = Blitem()
			labels = Blibb.get_label_from_template(bid)
			bitems = utils.get_items_from_request(labels, request)
			blitem_id = Blitem.insert(bid, user, bitems, tags)
			if utils.is_valid_id(blitem_id):
				cond = { 's': slug, 'u': username }
				Blibb.incNumItem(cond)
				utils.postProcess(blitem_id, bitems)
				res = {'id': blitem_id}
		else:
			res = {'error': ''}
	e.save()
	return jsonify(res)


def isAnonApp(key):
	for app in ANON_APPS:
		if key == app:
			return key
	return False


@mod.route('/<username>/<slug>', methods=['GET'])
@support_jsonp
def getBlibbBySlug(username=None, slug=None):	
	e = Event('web.user.blibb.getBlibbBySlug')
	if username is None:
		abort(404)
	if slug is None:
		abort(404)

	page = request.args.get('page',1)
	comments = request.args.get('comments',0)
	blibb =  Blibb.get_by_slug(username,slug)	
	ret = dict()
	cond = { 's': slug, 'u': username }
	Blibb.increase_view(cond, 'v')
	ret['blibb'] = blibb
	rs_items = Blitem.get_all_items(blibb['id'],int(page))
	# rs_items = json.loads(jitems)
	for i in rs_items:
		pass
	ret['items'] = rs_items['items']
	e.save()
	return  jsonify(ret)


@mod.route('/user/name/<user_name>', methods=['GET'])
@support_jsonp
def getUserByName(user_name=None):	
	e = Event('web.user.getUserByName')
	if user_name is None:
		abort(404)
	u = User.get_by_name(user_name)
	e.save()
	return jsonify(u)


@mod.route('/user/image', methods=['POST'])
@crossdomain(origin='*')
def setImageUser():	
	e = Event('web.user.setImageUser')
	user_id = request.form['object_id']
	image_id = request.form['image_id']
	if user_id is None:
		abort(404)
	if utils.is_valid_id(user_id):
		User.add_picture({'_id': ObjectId(user_id)}, image_id)	
	e.save()
	return 'ok'


@mod.route('/login', methods=['POST'])
@crossdomain(origin='*')
def doLogin():
	e = Event('web.user.doLogin')
	user = request.form['u']
	pwd = request.form['p']		
	key = User.authenticate(user,pwd)
	if key:
		d = dict()
		d['key'] = key
		e.save()
		return jsonify(d)
	else:
		e.save()
		abort(401)

@mod.route('/user', methods=['POST'])
@crossdomain(origin='*')
def newUser():
	e = Event('web.user.newUser')
	user = request.form['user']
	pwd = request.form['pwd']
	code = request.form['code']
	email = request.form['email']

	m = Manager()
	if m.validateCode(code):
		u_id = User.create(user, email, pwd, code)
		return jsonify({'id': u_id})
	else:
		return jsonify({'error': 'Code is not valid'})


@mod.route('/<username>/<slug>/tag/<tag>', methods=['GET'])
@support_jsonp
def get_items_by_tag(username=None, slug=None, tag=None):	
	e = Event('web.user.blibb.get_items_by_tag')

	if username is None:
		abort(404)
	if slug is None:
		abort(404)
	if tag is None:
		abort(404)

	ip = request.remote_addr
	e.addLog(ip)

	blibb_id = Blibb.get_id_by_slug(username,slug)
	cond = { 's': slug, 'u': username }
	Blibb.increase_view(cond, 'vt')
	
	# return blibb_id
	b = Blitem()
	items = b.getItemsByTag(blibb_id, tag)
	e.save()
	return  jsonify(items)

@mod.route('/<username>/<slug>/<id>', methods=['GET'])
@support_jsonp
def get_item_by_id(username=None, slug=None, id=None):
	e = Event('web.user.blibb.get_item_by_id')
	if username is None:
		abort(404)
	if slug is None:
		abort(404)
	if id is None:
		abort(404)

	blibb_id = Blibb.get_id_by_slug(username,slug)
	if utils.is_valid_id(id):
		if utils.is_valid_id(blibb_id):
			blitem = Blitem()
			items = Blitem.get_item({'_id': ObjectId(id), 'b': ObjectId(blibb_id)})
			e.save()
			return  jsonify(items)
		else:
			abort(404)
	else:
		return jsonify(Message.get('id_not_valid'))

