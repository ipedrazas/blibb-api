

import json
import redis
from flask import Blueprint, request, redirect, abort
from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.event.event import Event
from API.contenttypes.picture import Picture


mod = Blueprint('blibb', __name__, url_prefix='/blibb')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is blibb'"

##################
##### BLIBB  #####
##################

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
		
	user = getKey(key)
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
	user = getKey(key)
	if b.isOwner(blibb_id,user):
		res = b.addToBlibbGroup(blibb_id,userToAdd)
	else:
		d = dict()
		d['error'] = "Userkey is not valid for this operation"
		res = d
	e.save()
	return json.dumps(res)
	

@mod.route('/<blibb_id>/p/<params>', methods=['GET'])
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
	user = getKey(key)
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
	user = getKey(key)
	b = Blibb()
	res = dict()
	if b.isOwner(bid,user):
		b.remove(bid)
		res['result'] = 'success'
	else:
		res['error'] = 'You only can delete your own objects'
	e.save()
	return json.dumps(res)

def getKey(key):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	return r.get(key)