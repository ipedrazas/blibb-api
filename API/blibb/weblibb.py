

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

@mod.route('/meta/fields/<bid>', methods=['GET'])
def getBlibbFields(bid=None):
	if bid is not None:
		b = Blibb()
		fields = b.getFields(bid)
		return json.dumps(fields)

@mod.route('', methods=['POST'])
def newBlibb():
	e = Event('web.blibb.newBlibb')
	name = request.form['bname']
	desc = request.form['bdesc']
	template = request.form['btemplate'] 
	key = request.form['bkey']
	image_id = request.form['bimage']
	slug = request.form['slug']
	pict = Picture()
	if pict.isValidId(image_id):		
		image = pict.dumpImage(image_id)
	else:
		image = 'blibb.png'

	if request.form.get('bgroup', None) == "1":
		group = True
		if 'email_invites' in request.form:
			invites = request.form['email_invites'] 
		else:
			invites = ''
	else:
		group = False
		invites = ''
		
	user = utils.getKey(key)
	b = Blibb()
	res = b.insert(user, name, slug, desc, template, image, group, invites)
	e.save()
	return res

	

@mod.route('/adduser', methods=['POST'])
def addUserToBlibbGroup():	
	e = Event('web.blibb.addUserToBlibbGroup')
	b = Blibb()
	blibb_id = request.form['blibb_id']
	userToAdd = request.form['user']
	key = request.form['bkey']
	user = utils.getKey(key)
	if b.isOwner(blibb_id,user):
		res = b.addToBlibbGroup(blibb_id,userToAdd)
	else:
		d = dict()
		d['error'] = "Userkey is not valid for this operation"
		res = d
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
		return r
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
	r = b.getTemplateView(blibb_id, view_name)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

@mod.route('/<username>', methods=['GET'])
@support_jsonp
def getBlibbByUser(username=None):	
	e = Event('web.blibb.getBlibbByUser')
	b = Blibb()
	if username is None:
		abort(404)
	res = b.getByUser(username)
	e.save()
	return res


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
	key = request.form['k']
	bid = request.form['b']
	user = utils.getKey(key)
	b = Blibb()
	filter = {'_id': ObjectId(bid), 'u': user}
	b.remove(filter)
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