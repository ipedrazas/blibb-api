
from API.om.manager import Manager
from flask import Blueprint, request, abort, jsonify
from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('manager', __name__, url_prefix='/sys')


@mod.route('/validate/<code>', methods=['GET'])
@support_jsonp
def validate(code=None):
    return jsonify({'result': Manager.validateCode(code)})


@mod.route('/add/tobeta', methods=['POST'])
@crossdomain(origin='*')
def add_to_beta_list():
    email = request.form['email']
    ip = request.form['ip']
    browser = request.form['browser']

    res = {'result': Manager.addBetaUser(email, ip, browser)}
    return jsonify(res)


@mod.route('/add/code', methods=['POST'])
@crossdomain(origin='*')
def add_code():
    key = request.form['k']
    code = request.form['c']
    if key == 'ivan':
        res = {'result': Manager.addCode(code)}
        return jsonify(res)
    else:
        abort(401)
