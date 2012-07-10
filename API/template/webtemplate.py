
from flask import Blueprint, request, abort, jsonify, current_app

from API.template.template import Template
from API.template.ctrl_template import ControlTemplate
from API.event.event import Event
import API.utils as utils
from API.error import Message

template = Blueprint('template', __name__, url_prefix='/template')


@template.route('/<login_key>', methods=['GET'])
def get_all_templates(login_key=None):
    e = Event('web.get_all_templates')
    user = utils.get_user_name(login_key)
    templates = ControlTemplate.get_templates_by_user(user)
    e.save()
    return jsonify({'result': templates})


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
    name = request.form['template_name']
    desc = request.form['template_description']
    key = request.form['login_key']
    thumb = request.form['thumbnail']
    user = utils.get_user_name(key)
    # check if that template exists
    filter = {'n': name, 'u': user}
    current_app.logger.info(filter)
    template = ControlTemplate.get_object(filter, {'_id': 1})
    if template is None:
            res = ControlTemplate.insert(name, desc, user, thumb)
    else:
        res = str(template.get('_id', ''))
    e.save()
    return jsonify({'result': res})


@template.route('/controls', methods=['POST'])
def add_controls():
    e = Event('web.add_controls')
    template = request.form['template']
    controls = request.form['controls']
    key = request.form['login_key']
    user = utils.get_user_name(key)
    if utils.is_valid_id(template):
        res = ControlTemplate.add_controls(template, controls, user)
    else:
        jsonify(Message.get('id_not_valid'))

    e.save()
    return jsonify({'result': res})


@template.route('/pub', methods=['POST'])
def publishTemplate():
    e = Event('web.publishTemplate')
    template_id = request.form['template_id']
    view = request.form['view']
    key = request.form['login_key']
    user = utils.get_user_name(key)
    current_app.logger.info(template_id)
    template = ControlTemplate.get_by_id(template_id)
    current_app.logger.info(template)
    owner = template['owner']
    if owner == user:
        r = ControlTemplate.publish(view, template_id)
        if(r):
            res = {'result': 'ok'}
        else:
            res = {'error': 'Publishing failed'}
    else:
        res = {'error': 'Only the owner can publish'}
    e.save()
    return jsonify(res)


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
    user = utils.get_user_name(key)
    t = Template()
    if t.isOwner(t_id, user):
        res = t.addControl(c_id, t_id, title, help, order, view, slug, typex)
    else:
        res = {'error': 'User is not the owner of the Template'}
    e.save()
    return jsonify(res)
