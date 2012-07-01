
from API.om.manager import Manager
from API.event.event import Event
import API.utils as utils

from flask import Blueprint, request, redirect, abort, current_app, jsonify
from functools import wraps
import json

from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('manager', __name__, url_prefix='/sys')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is Manager'"

@mod.route('/validate/<code>', methods=['GET'])
def validate(code=None):
	m = Manager()
	return jsonify({'result':m.validateCode(code)})

@mod.route('/add/tobeta', methods=['POST'])
@crossdomain(origin='*')
def add_to_beta_list():
	e = Event('web.wmanager.add_to_beta_list')
	email = request.form['email']
	ip = request.form['ip']
	browser = request.form['browser']
	m = Manager()
	res = {'result': m.addBetaUser(email,ip,browser)}
	e.save()
	return jsonify(res)

@mod.route('/add/code', methods=['POST'])
@crossdomain(origin='*')
def add_code():
	e = Event('web.wmanager.add_code')
	key = request.form['k']
	code = request.form['c']
	if key == 'ivan':
		m = Manager()
		res = {'result': m.addCode(code)}
		return jsonify(res)
	else:
		abort(401)