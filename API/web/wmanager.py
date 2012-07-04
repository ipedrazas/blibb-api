
from API.om.manager import Manager
from API.event.event import Event

from flask import Blueprint, request, redirect, abort, current_app, jsonify
from functools import wraps
import json

from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('manager', __name__, url_prefix='/sys')



@mod.route('/validate/<code>', methods=['GET'])
def validate(code=None):
	return jsonify({'result': Manager.validateCode(code)})

@mod.route('/add/tobeta', methods=['POST'])
@crossdomain(origin='*')
def add_to_beta_list():
	e = Event('web.wmanager.add_to_beta_list')
	email = request.form['email']
	ip = request.form['ip']
	browser = request.form['browser']

	res = {'result': Manager.addBetaUser(email,ip,browser)}
	e.save()
	return jsonify(res)

@mod.route('/add/code', methods=['POST'])
@crossdomain(origin='*')
def add_code():
	e = Event('web.wmanager.add_code')
	key = request.form['k']
	code = request.form['c']
	if key == 'ivan':
		res = {'result': Manager.addCode(code)}
		e.save()
		return jsonify(res)
	else:
		abort(401)