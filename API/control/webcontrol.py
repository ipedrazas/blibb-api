
from flask import Blueprint, request, redirect, abort, jsonify

from API.control.bcontrol import BControl, Control

from API.event.event import Event
from API.decorators import crossdomain
from API.decorators import support_jsonp

import API.utils as utils

mod = Blueprint('control', __name__, url_prefix='')


@mod.route('/control', methods=['POST'])
@crossdomain(origin='*')
def new_control():
	e = Event('web.new_control')
	key = request.form['login_key']
	name = request.form['control_name']
	ui = request.form['control_ui']
	type = request.form['control_type']
	default = request.form['default']
	button = request.form['button']
	
	user = utils.get_key(key)
	cid = Control.insert(name, user, ui, type, default, button)
	res = {'id': cid}
	e.save()
	return jsonify(res)



@mod.route('/ctrls/all', methods=['GET'])
def getAllControls():
	e = Event('web.getAllControls')
	c = BControl()
	res = c.getAllControls()
	e.save()
	return res 


@mod.route('/controls', methods=['GET'])
def get_controls():
	e = Event('web.get_controls')
	res = Control.get_all_controls()
	e.save()
	return jsonify({'controls': res})


@mod.route('/ctrl/ui/<c_id>', methods=['GET'])
def getCtrlUi(c_id=None):
	e = Event('web.getCtrlUi')
	c = BControl()
	res = c.getUiDefTemplate(c_id)
	return res

@mod.route('/ctrl/view/<c_id>', methods=['GET'])
def getCtrlView(c_id=None):
	e = Event('web.getCtrlView')
	if c_id is not None:
		c = BControl()
		viewTemplate = c.getViewTemplate(c_id)
		res = json.dumps(viewTemplate, default=json_util.default)
	else:
		res = getMessage('0',True,'count')
	return res