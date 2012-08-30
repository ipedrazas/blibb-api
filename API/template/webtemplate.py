
from flask import Blueprint, request, abort, jsonify, current_app

from API.template.template import Template
from API.template.ctrl_template import ControlTemplate
import API.utils as utils
from API.error import Message

template = Blueprint('template', __name__, url_prefix='/template')


@template.route('/<login_key>', methods=['GET'])
def get_all_templates(login_key=None):
    user = utils.get_user_name(login_key)
    templates = ControlTemplate.get_templates_by_user(user)
    return jsonify({'result': templates})


@template.route('/<status>/<params>', methods=['GET'])
def getTemplates(status=None, params=None):
    template = Template()
    res = template.getActiveTemplates(status, params)
    return res


@template.route('', methods=['POST'])
def newTemplate():
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
    return jsonify({'result': res})


@template.route('/controls', methods=['POST'])
def add_controls():
    template = request.form['template']
    controls = request.form['controls']
    key = request.form['login_key']
    user = utils.get_user_name(key)
    res = 'Something went wrong'
    current_app.logger.info('controls' + str(controls))
    # if utils.is_valid_id(template):
    res = ControlTemplate.add_controls(template, controls, user)
    # else:
    #     jsonify(Message.get('id_not_valid'))
    return jsonify({'result': res})


@template.route('/pub', methods=['POST'])
def publishTemplate():
    template_id = request.form['template_id']
    key = request.form['login_key']
    user = utils.get_user_name(key)
    template = ControlTemplate.get_by_id(template_id)
    owner = template['owner']
    if owner == user:
        r = ControlTemplate.publish_default(template_id)
        if(r):
            res = {'result': 'ok'}
        else:
            res = {'error': 'Publishing failed'}
    else:
        res = {'error': 'Only the owner can publish'}
    return jsonify(res)


@template.route('/<template_id>', methods=['GET'])
def getTemplate(template_id=None):
    t = Template()
    res = t.getById(template_id)
    if res != 'null':
        return res
    else:
        abort(404)


@template.route('/add', methods=['POST'])
def addControl():
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
    return jsonify(res)
