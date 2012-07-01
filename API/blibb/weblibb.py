

import json
from flask import Blueprint, request, redirect, abort, jsonify
from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.event.event import Event
from API.contenttypes.picture import Picture
import API.utils as utils
from bson.objectid import ObjectId

from API.decorators import crossdomain
from API.decorators import support_jsonp

import logging

mod = Blueprint('blibb', __name__, url_prefix='/blibb')

logger = logging.getLogger('twitter_worker')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


@mod.route('/hi')
def hello_world():
	return "Hello World, this is blibby'"

@mod.route('/meta/webhooks/<bid>', methods=['GET'])
def getWebhooks(bid=None):
	if utils.isValidId(bid):
		b = Blibb()
		fields = b.getWebhooks(bid)
		return jsonify({'webhooks': fields})
	else:
		return jsonify({'error': 'Object id not valid'})

@mod.route('/meta/fields/<bid>', methods=['GET'])
def getBlibbFields(bid=None):
	if bid is not None:
		fields = Blibb.getFields(bid)
		return jsonify({'fields':fields})

@mod.route('', methods=['POST'])
def newBlibb():
	e = Event('web.blibb.newBlibb')
	name = request.form['bname']
	desc = request.form['bdesc']
	template = request.form['btemplate'] 
	key = request.form['bkey']
	user = utils.getKey(key)
	image_id = request.form['bimage']
	slug = request.form['slug']
	write_access = request.form['write_access']
	read_access = request.form['read_access']

	# check if a blibb with that slug already exists
	if not Blibb.getIdBySlug(user,slug):
		pict = Picture()
		if utils.isValidId(image_id):		
			image = pict.dumpImage(image_id)
		else:
			image = 'blibb.png'

		new_id = Blibb.insert(user, name, slug, desc, template, image, read_access, write_access)
		res = {'id': new_id}
	else:
		res = {'error': 'Blibb with that slug already exists'}

	e.save()
	return jsonify(res)	
	

@mod.route('/<blibb_id>/p/<params>', methods=['GET'])
@crossdomain(origin='*')
def getBlibb(blibb_id=None,params=None):
	e = Event('web.blibb.getBlibb')
	if blibb_id is None:
		abort(404)
	b = Blibb()
	if params is None:
		r = b.getById(blibb_id)
	else:
		r = b.getByIdParams(blibb_id,params)

	e.save()
	if r != 'null':
		return jsonify(r)
	else:
		abort(404)

@mod.route('/<blibb_id>/template', methods=['GET'])
@crossdomain(origin='*')
def getBlibbTemplate(blibb_id=None):
	e = Event('web.blibb.getBlibbTemplate')
	b = Blibb()
	r = b.getTemplate(blibb_id)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

@mod.route('/<blibb_id>/view', methods=['GET'])
@mod.route('/<blibb_id>/view/<view_name>', methods=['GET'])
def getBlibbView(blibb_id=None, view_name='null'):
	e = Event('web.blibb.getBlibbView')
	b = Blibb()
	if utils.isValidId(blibb_id):
		r = Blibb.getTemplateView(blibb_id, view_name)
		e.save()
		if r != 'null':
			return jsonify(r)
		else:
			abort(404)
	else:
		abort(400)

@mod.route('/<username>', methods=['GET'])
@support_jsonp
def getBlibbByUser(username=None):	
	e = Event('web.blibb.getBlibbByUser')
	b = Blibb()
	if username is None:
		abort(404)
	res = b.getByUser(username)
	e.save()
	return jsonify(res)


@mod.route('/<username>/group', methods=['GET'])
def getGroupBlibbByUser(username=None):	
	e = Event('web.blibb.getGroupBlibbByUser')
	b = Blibb()
	if username is None:
		abort(404)
	res = b.getByGroupUser(username)
	e.save()
	return res


#####################
####### TAGS  #######
#####################

@mod.route('/tag', methods=['POST'])
def newTag():
	e = Event('web.blibb.newTag')
	target_id = None
	target = None
	key = request.form['k']
	user = utils.getKey(key)
	target_id = request.form['b']
	target = Blibb()	

	if target.isOwner(target_id,user):
		tag = request.form['t']
		t = target.addTag(target_id, tag)

	e.save()
	return json.dumps('ok')

@mod.route('/del', methods=['POST'])
def deleteBlibb():
	e = Event('web.blibb.deleteBlibb') 
	key = request.form['login_key']
	bid = request.form['blibb_id']
	user = utils.getKey(key)
	
	if utils.isValidId(bid):
		filter = {'_id': ObjectId(bid), 'u': user}
		Blibb.remove(filter)
	e.save()
	return jsonify({'ret': 1})

########################
####### FOLLOWERS ######
########################

@mod.route('/fol', methods=['POST'])
def addFollower():
	e = Event('web.blibb.addFollower') 
	key = request.form['k']
	bid = request.form['b']
	follow= request.form['f']
	user = utils.getKey(key)
	b = Blibb()
	res = dict()
	if b.isOwner(bid,user):		
		res['error'] = 'You are always your first follower!'
	else:
		b.addFollower(bid, follow)
		res['result'] = 'Ok'
	e.save()
	return jsonify(res)


@mod.route('/action/image', methods=['POST'])
@crossdomain(origin='*')
def updateImage():
	e = Event('web.blibb.updateImage')
	object_id = request.form['object_id']
	image_id = request.form['image_id']
	if object_id is None:
		abort(404)
	b = Blibb()
	b.addPicture({'_id': ObjectId(object_id)}, image_id)	
	e.save()
	return 'ok'

@mod.route('/actions/webhook', methods=['POST'])
@crossdomain(origin='*')
def addWebhook():
	e = Event('web.blibb.addWebhook')
	key = request.form['login_key']
	bid = request.form['blibb_id']
	callback = request.form['callback']
	fields = request.form['fields']
	action = request.form['action']
	user = utils.getKey(key)
	res = dict()
	wb = {'a': action, 'u': callback, 'f': fields}
	if utils.isValidId(bid):
		b = Blibb()
		if b.isOwner(bid,user):
			Blibb.addWebhook(bid, wb)
			res['result'] = 'ok'
		else:
			abort(401)
	else:
		res['error'] = 'Object Id is not valid'
	
	e.save()
	return jsonify(res)


