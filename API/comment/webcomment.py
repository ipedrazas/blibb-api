

import json
import redis
from flask import Blueprint, request, redirect, abort
from API.comment.comment import Comment
from API.event.event import Event
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from bson import json_util
import logging

mod = Blueprint('comment', __name__, url_prefix='/comment')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is comment'"


#####################
##### COMMENTS  #####
#####################

@mod.route('', methods=['POST'])
def newComment():
	e = Event('web.newComment')
	comment = Comment()
	c_id = None
	key = request.form['k']
	user = getKey(key)
	logging.error('Processing %s' % user)
	if user is not None:
		target_id = None
		parent = None
		pObject = None
		if 'b' in request.form:		
			target_id = request.form['b']
			parent = 'b'
			pObject = Blibb()
			logging.error('Processing %s' % target_id)
		elif 'i' in request.form:
			target_id = request.form['i']
			parent = 'i'
			pObject = Blitem()
			logging.error('Processing %s' % target_id)
		else:
			abort(404)
		
		text =  request.form['c']
		c_id = comment.insert(target_id, user, text, parent)
		pObject.incCommentsCounter(target_id)
		e.save()
	else:
		d = dict()
		d['error'] = "user not found"
		c_id = d
	return json.dumps(c_id,default=json_util.default)



@mod.route('/<parent_id>', methods=['GET'])
def getComments(parent_id=None):
	e = Event('web.getComments')
	comment = Comment()
	cs = comment.getCommentsById(parent_id,True)
	e.save()
	return cs

def getKey(key):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	return r.get(key)