#
#


from flask import Blueprint, request, abort, jsonify, g, current_app, render_template
from API.oiapp.models import User, Audit, Oi
from API.event.event import Event

from API.utils import get_user, get_user_name
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

@oiuser.errorhandler(401)
@crossdomain(origin='*')
def custom_401(error):
     return render_template('401.html'), 401

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
    if 'error' in doc:
        abort(409, 'User already exists')
    else:
        Audit.signup(username, '')
        return jsonify({'user': User.to_safe_dict(doc)})

@oiuser.route('/facebook', methods=['POST'])
@crossdomain(origin='*')
def new_user_facebook():
    username = request.form['username']
    fbid = request.form['fbid']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    timezone = request.form['timezone']
    email = request.form['email']
    img = "http://graph.facebook.com/" + request.form['fbid'] + "/picture"

    doc = User.create_facebook(username, fbid, email, first_name, last_name, timezone, img)
    user = User.login_facebook(fbid)
    if 'error' in doc:
        print str(doc)
        abort(409, 'User already exists')
    else:
        Audit.signup(username, '')
        return jsonify(user) if user else abort(401)


@oiuser.route('/<username>', methods=['GET'])
@support_jsonp
def get_oi_user(username):
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


@oiuser.route('/loginfb', methods=['POST'])
@crossdomain(origin='*')
def do_login_facebook():
    username = request.form['fbid']
    user = User.login_facebook(username)
    Audit.login_facebook(username, '')
    return jsonify(user) if user else abort(401)

@oiuser.route('/logout', methods=['POST'])
@crossdomain(origin='*')
def do_logout():
    login_key = request.form['login_key']
    user = User.logout(login_key)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)


@oiuser.route('/mail/subs', methods=['POST'])
@crossdomain(origin='*')
def set_mail_subscription():
    login_key = request.form['login_key']
    user = get_user(login_key)
    current_app.logger.info('set_mail_subscription' + ":" + str(user) + ":" + login_key)
    User.set_mail_subscription(user)
    return jsonify({'subscription': not user.get('m_subs', False)})



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


# @oiuser.route('/<username>/config/app', methods=['GET'])
# @support_jsonp
# @parse_args
# def get_config(username, *args, **kwargs):

