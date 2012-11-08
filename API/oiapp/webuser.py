#
#


from flask import Blueprint, request, abort, jsonify, g, current_app
from API.oiapp.models import User, Audit, Oi
from API.event.event import Event

from API.utils import get_user_name
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
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    device_id = ''
    if 'device' in request.form:
        device_id = request.form['device']
    doc = User.create(username, password, email, device_id)
    Audit.signup(username, '')
    return jsonify({'user': User.to_safe_dict(doc)})


@oiuser.route('/<username>', methods=['GET'])
@support_jsonp
def get_user(username):
    doc = User.get({'$or': [{'username': username.strip()}, {'email': username.strip()}]})
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
    username = get_user_name(login_key)
    pwd = request.form['password']
    old_password = request.form['old_password']
    user = User.change_password(username, pwd, old_password)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)


@oiuser.route('/login', methods=['POST'])
@crossdomain(origin='*')
def do_login():
    username = request.form['username']
    pwd = request.form['password']
    user = User.authenticate(username, pwd)
    Audit.login(username, '')
    return jsonify(User.to_safe_dict(user)) if user else abort(401)


@oiuser.route('/logout', methods=['POST'])
@crossdomain(origin='*')
def do_logout():
    login_key = request.form['login_key']
    user = User.logout(login_key)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)
    

@oiuser.route('/<username>/invitations', methods=['GET'])
@support_jsonp
@parse_args
def get_invitations_by_user(username, *args, **kwargs):
    resultset = []
    senders = []
    subscribers = []
    invited = []
    user = User.get_by_name(username)
    current_app.logger.info(user)
    if user and 'sub_email' in user:
        docs = Oi.get_all({'invited': {'$in': user['sub_email']}}, **kwargs)
        for doc in docs:
            resultset.append(Oi.to_dict(doc))
        return jsonify({'resultset': resultset})
    abort(404)