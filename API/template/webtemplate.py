
from flask import Blueprint, request, redirect, abort

import json
from bson import json_util

from API.template.template import Template
from API.event.event import Event
import API.utils as utils


mod = Blueprint('template', __name__, url_prefix='/template')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is template'"

@mod.route('/<status>/<params>', methods=['GET'])
def getTemplates(status=None, params=None):
	e = Event('web.newTemplate')
	template = Template()
	res = template.getActiveTemplates(status, params)
	e.save()
	return res

@mod.route('', methods=['POST'])
def newTemplate():
	e = Event('web.newTemplate')
	name = request.form['bname']
	desc = request.form['bdesc']
	key = request.form['bkey']
	status = request.form['bstatus']
	thumb = request.form['thumbnail']
	user = utils.getKey(key)
	t = Template()
	res = str(t.insert(name, desc, user, thumb, status))
	e.save()
	return res
	
@mod.route('/pub', methods=['POST'])
def publishTemplate():	
	e = Event('web.publishTemplate')
	t_id = request.form['tid']
	view = request.form['view']
	key = request.form['k']
	user = utils.getKey(key)
	t = Template()
	if t.isOwner(t_id, user):
		t.load(t_id)
		t.createDefaultView()
		res = getMessage(t_id, True)
	else:
		res = getErrorMessage('User is not the owner of the Template')
	e.save()
	return res

@mod.route('/<template_id>', methods=['GET'])
def getTemplate(template_id=None):	
	e = Event('web.getTemplate')
	t = Template()
	res = t.getById(template_id)
	e.save()
	if res != 'null':
		return res
	else:
		abort(404)

@mod.route('/add', methods=['POST'])
def addControl():
	e = Event('web.addControl')
	c_id = request.form['cid']
	t_id = request.form['tid']
	order = request.form['order']
	title = request.form['title']
	help = request.form['help']
	view = request.form['view']
	slug = request.form['slug']
	typex = request.form['typex']
	key = request.form['k']
	user = utils.getKey(key)
	t = Template()
	if t.isOwner(t_id, user):
		res = t.addControl(c_id, t_id, title, help, order, view, slug, typex)
	else:
		res = getErrorMessage('User is not the owner of the Template')
	e.save()
	return res


def getMessage(message, asJson=True, key='response'):
		res = dict()
		res[key] = message
		if asJson:
			return json.dumps(res)
		else:
			return res