
from API.user.buser import User
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from API.event.event import Event
from API.control.bcontrol import BControl
import API.utils as utils

from flask import Blueprint, request, redirect, abort, current_app, jsonify
from functools import wraps
import json
from API.utils import crossdomain


mod = Blueprint('user', __name__, url_prefix='')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is user'"



def check_tokens(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		app_token = request.args.get('app_token', False)
		user_token = request.args.get('user_token', False)
		if app_token or user_token:
			pass
		else:
			abort(401)
	return decorated_function

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


#####################
###### USERS  #######
#####################

@mod.route('/<username>/<slug>', methods=['POST'])
@crossdomain(origin='*')
@support_jsonp
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
	return jsonify(blitem_id)

@mod.route('/cors',methods=['GET'])
@crossdomain(origin='*')
def getCors():
	return jsonify(foo='yayyyy cross domain ftw')

@mod.route('/<username>/<slug>', methods=['GET'])
@support_jsonp
@crossdomain(origin='*')
def getBlibbBySlug(username=None, slug=None):	
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
	return  jsonify(ret)


@mod.route('/user/name/<user_name>', methods=['GET'])
@support_jsonp
def getUserByName(user_name=None):	
	e = Event('web.user.getUserByName')
	if user_name is None:
		abort(404)
	user = User()
	u = user.getByName(user_name)
	
	e.save()
	return jsonify(u)

@mod.route('/user/<user_id>', methods=['GET'])
@support_jsonp
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
@support_jsonp
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


@mod.route('/login', methods=['GET','POST'])
@support_jsonp
def doLogin():
	
	if request.method == 'POST':
		user = request.form['u']
		pwd = request.form['p']
	else:
		user = request.args.get('u', '')
		pwd = request.args.get('p', '')
		
	u = User()
	key = u.authenticate(user,pwd)
	if key:
		d = dict()
		d['key'] = key
		return jsonify(d)
	else:
		abort(401)


@mod.route('/invite/<code>', methods=['GET'])
def validateInviteCode(code=None):	
	e = Event('web.user.validateInviteCode')
	if code is None:
		abort(404)
	user = User()
	u = user.getByName(user_name)
	
	e.save()
	return jsonify(u)