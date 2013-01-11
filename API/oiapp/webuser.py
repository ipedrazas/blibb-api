#
#


from flask import Blueprint, request, abort, jsonify, g, current_app, render_template
from API.oiapp.models import User, Audit, Oi
from API.event.event import Event
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
    device = request.form.get("origin", None)
    doc = User.create(username, password, email, device)
    if 'error' in doc:
        abort(409, 'User already exists')
    else:
        Audit.signup(username, '')
        return jsonify({'user': User.to_safe_dict(doc)})

@oiuser.route('/<username>', methods=['POST'])
@crossdomain(origin='*')
def update(username):
    current_app.logger.info('update')
    login_key = request.form['login_key']
    user = User.get_user(login_key)
    if username == user.get('username', False):
        first_name = request.form.get('first_name', None)
        last_name = request.form.get('last_name', None)
        timezone = request.form.get('timezone', None)
        img_url = request.form.get('img_url', None)
        updated_user = {}
        if first_name:
            updated_user['first_name'] = first_name
        if last_name:
            updated_user['last_name'] = last_name
        if timezone:
            updated_user['timezone'] = timezone
        if img_url:
            updated_user['img'] = img_url
        User.update(username, updated_user)
        return jsonify({'result': {'code': 1, 'msg': 'Object updated'}})
    else:
        abort(401)


@oiuser.route('/facebook', methods=['POST'])
@crossdomain(origin='*')
def new_user_facebook():
    current_app.logger.info('facebook')
    username = request.form['username']
    fbid = request.form['fbid']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    timezone = request.form['timezone']
    email = request.form['email']
    img = "http://graph.facebook.com/" + request.form['fbid'] + "/picture"
    device = request.form.get("origin", None)
    doc = User.create_facebook(username, fbid, email, first_name, last_name, timezone, img)
    user = User.login_facebook(fbid)
    if 'error' in doc:
        print str(doc)
        abort(409, 'User already exists')
    else:
        Audit.facebook_signup(username, device)
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


@oiuser.route('/<username>/password', methods=['POST'])
@crossdomain(origin='*')
def change_password(username):
    login_key = request.form['login_key']
    user = User.get_user(login_key)
    if user:
        if username == user['username']:
            pwd = request.form['password']
            old_password = request.form.get('old_password', '')
            res = User.change_password(username, pwd, old_password)
            current_app.logger.info(str(res))
            return jsonify({'result': {'code': 'true', 'msg': 'Password updated'}}) if res else abort(401)
    abort(401)

@oiuser.route('/login', methods=['POST'])
@crossdomain(origin='*')
def do_login():
    username = request.form['username']
    pwd = request.form['password']
    origin = request.form.get("origin", None)
    user = User.authenticate(username, pwd)
    Audit.login(username, origin)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)


@oiuser.route('/loginfb', methods=['POST'])
@crossdomain(origin='*')
def do_login_facebook():
    username = request.form['fbid']
    user = User.login_facebook(username)
    origin = request.form.get("origin", None)
    Audit.login_facebook(username, origin)
    return jsonify(user) if user else abort(401)


@oiuser.route('/<username>/logout', methods=['POST'])
@crossdomain(origin='*')
def do_logout(username):
    login_key = request.form['login_key']
    user = User.get_user(login_key)
    if user['username'] == username:
        off = User.logout(login_key)
        return jsonify(User.to_safe_dict(user)) if off else abort(401)
    abort(401)

@oiuser.route('/<username>/mailsubs', methods=['POST'])
@crossdomain(origin='*')
def set_mail_subscription(username):
    login_key = request.form['login_key']
    user = User.get_user(login_key)
    if username == user['username']:
        res = User.set_mail_subscription(login_key, username)
        return jsonify({'subscription': res})
    abort(401)



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

