
from flask import Blueprint, request, redirect, abort

import json
from bson import json_util

from API.control.bcontrol import BControl
from API.event.event import Event


mod = Blueprint('control', __name__, url_prefix='')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is control'"

@mod.route('/ctrls/all', methods=['GET'])
def getAllControls():
	e = Event('web.getAllControls')
	c = BControl()
	res = c.getAllControls()
	e.save()
	return res 


@mod.route('/ctrls', methods=['GET'])
def getCtrls():
	e = Event('web.getCtrls')
	c = BControl()
	res = c.getIdNameList()
	e.save()
	return res


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