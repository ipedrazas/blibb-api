
from flask import Blueprint, request, redirect, abort, jsonify

from API.template.template import Template
from API.template.ctrl_template import ControlTemplate
from API.event.event import Event
import API.utils as utils
from API.error import Message

template = Blueprint('template', __name__, url_prefix='/template')




@template.route('/<status>/<params>', methods=['GET'])
def getTemplates(status=None, params=None):
	e = Event('web.newTemplate')
	template = Template()
	res = template.getActiveTemplates(status, params)
	e.save()
	return res

@template.route('', methods=['POST'])
def newTemplate():
	e = Event('web.newTemplate')
	name = request.form['name']
	desc = request.form['description']
	key = request.form['login_key']
	thumb = request.form['thumbnail']
	user = utils.getKey(key)
	t = Template()
	res = ControlTemplate.insert(name, desc, user, thumb)
	e.save()
	return jsonify({'result': res})

@template.route('/controls', methods=['POST'])
def add_controls():
	e = Event('web.add_controls')
	template = request.form['template']
	controls = request.form['controls']
	key = request.form['login_key']
	user = utils.getKey(key)
	if utils.is_valid_id(template):	
		res = ControlTemplate.add_controls(template, controls, user)
	else:
		jsonify(Message.get('id_not_valid'))
	
	e.save()
	return jsonify({'result': res})
	
@template.route('/pub', methods=['POST'])
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

@template.route('/<template_id>', methods=['GET'])
def getTemplate(template_id=None):	
	e = Event('web.getTemplate')
	t = Template()
	res = t.getById(template_id)
	e.save()
	if res != 'null':
		return res
	else:
		abort(404)

@template.route('/add', methods=['POST'])
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

