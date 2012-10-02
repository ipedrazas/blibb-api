#
#


from flask import Blueprint, request, abort, jsonify, g
from API.oiapp.models import User
from API.event.event import Event


from API.utils import get_email, queue_ducksboard_delta
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.decorators import parse_args


oiuser = Blueprint('oiuser', __name__, url_prefix='/users')


@oiuser.before_request
def before_request():
    g.e = Event(request.path)


@oiuser.teardown_request
def teardown_request(exception):
    g.e.save()


@oiuser.route('', methods=['POST'])
@crossdomain(origin='*')
def new_user():
    email = request.form['email']
    password = request.form['password']
    device_id = ''
    if 'device' in request.form:
        device_id = request.form['device']
    doc = User.create(email, password, device_id)
    queue_ducksboard_delta('80347')
    return jsonify({'user': User.to_safe_dict(doc)})


@oiuser.route('/<email>', methods=['GET'])
@support_jsonp
def get_user(email):
    doc = User.get({'email': email})
    return jsonify({'user': User.to_safe_dict(doc)})


@oiuser.route('', methods=['GET'])
@support_jsonp
@parse_args
def get_users(*args, **kwargs):
    resultset = []
    docs = User.get_all(*args, **kwargs)
    for doc in docs:
        resultset.append(User.to_safe_dict(doc))

    return jsonify({'resultset': resultset})


@oiuser.route('/password', methods=['POST'])
@crossdomain(origin='*')
def change_password():
    login_key = request.form['login_key']
    email = get_email(login_key)
    pwd = request.form['password']
    old_password = request.form['old_password']
    user = User.change_password(email, pwd, old_password)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)


@oiuser.route('/login', methods=['POST'])
@crossdomain(origin='*')
def do_login():
    user = request.form['email']
    pwd = request.form['password']
    user = User.authenticate(user, pwd)
    queue_ducksboard_delta('80360')
    return jsonify(User.to_safe_dict(user)) if user else abort(401)


@oiuser.route('/logout', methods=['POST'])
@crossdomain(origin='*')
def do_logout():
    login_key = request.form['login_key']
    user = User.logout(login_key)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)
