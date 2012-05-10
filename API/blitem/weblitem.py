


import logging
import redis
from flask import Blueprint, request, redirect, abort

from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.event.event import Event
from API.control.bcontrol import BControl
from API.contenttypes.bookmark import Bookmark
import API.utils as utils
from bson.objectid import ObjectId

mod = Blueprint('blitem', __name__, url_prefix='/blitem')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is blitem'"


####################
##### BLITEMS  #####
####################

@mod.route('', methods=['POST'])
def newItem():
	e = Event('web.blitem.newItem')
	bid = request.form['b']
	key = request.form['k']
	tags = request.form['tags']

	user = getKey(key)
	bitems = []
	b = Blibb()
	labels = b.getLabelFromTemplate(bid)
	logging.error(labels)
	blitem = Blitem()
	for key,value in request.form.iteritems():
		if '-' in key:
			elem = getBlitemFromRequest(key, value, labels, user, bid)
			bitems.append(elem)

	blitem_id = blitem.insert(bid, user, bitems, tags)
	postProcess(blitem_id, bitems)
	e.save()
	return blitem_id

@mod.route('/fields/<blibb_id>', methods=['GET'])
def getBlitemFields(username=None):	
	e = Event('web.blibb.getGroupBlibbByUser')
	b = Blibb()
	res = b.getLabelFromTemplate(blibb_id)
	e.save()
	return json.dumps(res)


@mod.route('/read/<blitem_id>', methods=['GET'])
def getReadViewItems(blitem_id=None):
	e = Event('web.blitem.getReadViewItems')
	i = Blitem()
	r = i.getById(blitem_id)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)


@mod.route('/<blitem_id>', methods=['GET'])
def getBlitem(blitem_id=None):
	e = Event('web.blitem.getBlitem')
	i = Blitem()
	r = i.getFlat(blitem_id)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

@mod.route('/tag', methods=['POST'])
def newTag():
	e = Event('web.blitem.newTag')
	target_id = None
	target = None
	key = request.form['k']
	user = getKey(key)
	target_id = request.form['i']
	target = Blitem()

	if target.isOwner(target_id,user):
		tag = request.form['t']
		t = target.addTag(target_id, tag)

	e.save()
	return json.dumps('ok')


@mod.route('/<blibb_id>/blitems', methods=['GET'])
def getAllItems(blibb_id=None):
	e = Event('web.blitem.getAllItems')
	i = Blitem()
	its = i.getAllItems(blibb_id)
	r = i.resultSetToJson(its)
	e.save()
	return r

@mod.route('/<blibb_id>/items', methods=['GET'])
def getAllItemsFlat(blibb_id=None):
	e = Event('web.blitem.getAllItemsFlat')
	i = Blitem()
	r = i.getAllItemsFlat(blibb_id)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

@mod.route('/<blibb_id>/v/<view>', methods=['GET'])
def getItemsByBlibbAndView(blibb_id=None,view='Default'):
	# This method returns all the blitems
	# by blibb and rendered with the view 
	# passed
	e = Event('web.blitem.getItemsByBlibbAndView')
	b = Blibb()
	r = b.getTemplateView(blibb_id, view)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

def getKey(key):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	return r.get(key)

def getBlitemFromRequest(key, value, labels, user, bid):
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

def postProcess(obj_id, items):
	for blitem in items:
		# print blitem
		typex = blitem['t']
		if BControl.isURL(typex):
			utils.sendUrl(obj_id,blitem['v'])

