


import logging
import redis
from flask import Blueprint, request, redirect, abort, jsonify

from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.event.event import Event
from API.control.bcontrol import BControl
from API.contenttypes.bookmark import Bookmark
import API.utils as utils
from bson.objectid import ObjectId
import API.utils as utils
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.error import Message


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

	user = utils.getKey(key)
	if utils.isValidId(bid):
		b = Blibb.getObject({'_id': ObjectId(bid)},{'u':1,'t.i.n': 1, 't.i.s': 1})
		owner = b.get('u')
		if owner == user:
			labels = Blibb.getLabels(b.get('t'))
			blitem = Blitem()
			bitems = utils.getItemsFromRequest(labels, request)

			blitem_id = blitem.insert(bid, user, bitems, tags)
			if blitem_id:
				cond = {'_id': ObjectId(bid)}
				Blibb.incNumItem(cond)
			utils.postProcess(blitem_id, bitems)
			e.save()
			return blitem_id
		else:
			abort(401)
	return jsonify(Message.get('id_not_valid'))

@mod.route('/fields/<blibb_id>', methods=['GET'])
@crossdomain(origin='*')
def getBlitemFields(blibb_id=None):	
	e = Event('web.blibb.getBlitemFields')
	if utils.isValidId(blibb_id):
		b = Blibb.getObject({'_id': ObjectId(blibb_id)},{'u':1,'t.i.n': 1, 't.i.s': 1})
		res = Blibb.getLabels(b.get('t'))
	else:
		res = Message.get('id_not_valid')
	e.save()
	return jsonify(res)


@mod.route('/<blitem_id>', methods=['GET'])
@crossdomain(origin='*')
def getBlitem(blitem_id=None):
	e = Event('web.blitem.getBlitem')
	i = Blitem()
	r = i.getFlat(blitem_id)
	e.save()
	if r != 'null':
		return jsonify(r)
	else:
		abort(404)

@mod.route('/tag', methods=['POST'])
def newTag():
	e = Event('web.blitem.newTag')
	target_id = None
	target = None
	key = request.form['k']
	user = utils.getKey(key)
	target_id = request.form['i']
	target = Blitem()

	if target.isOwner(target_id,user):
		tag = request.form['t']
		t = target.addTag(target_id, tag)

	e.save()
	return jsonify({'response': 'ok'})


@mod.route('/<blibb_id>/blitems', methods=['GET'])
def getAllItems(blibb_id=None):
	e = Event('web.blitem.getAllItems')
	i = Blitem()
	its = i.getAllItems(blibb_id)	
	e.save()
	return jsonify(its)

@mod.route('/<blibb_id>/items', methods=['GET'])
def getAllItemsFlat(blibb_id=None, page=1):
	e = Event('web.blitem.getAllItemsFlat')
	i = Blitem()
	r = i.getAllItemsFlat(blibb_id, page)
	e.save()
	if r != 'null':
		return jsonify(r)
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

