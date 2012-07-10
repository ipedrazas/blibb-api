
from flask import Blueprint, request, jsonify

from API.control.bcontrol import BControl, Control

from API.event.event import Event
from API.decorators import crossdomain
from API.decorators import support_jsonp

import API.utils as utils

mod = Blueprint('control', __name__, url_prefix='')


@mod.route('/controls', methods=['POST'])
@crossdomain(origin='*')
def new_control():
    e = Event('web.new_control')
    key = request.form['login_key']
    name = request.form['control_name']
    ui = request.form['control_ui']
    type = request.form['control_type']
    default = request.form['control_ui']
    button = request.form['control_button']

    user = utils.get_user_name(key)
    cid = Control.insert(name, user, ui, type, default, button)
    res = {'id': cid}
    e.save()
    return jsonify(res)


@mod.route('/ctrls/all', methods=['GET'])
@support_jsonp
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
    e.save()
    return res
