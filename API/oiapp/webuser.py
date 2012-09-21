#
#


from flask import Blueprint, request, abort, jsonify, g
from API.oiapp.models import User
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
    login_key = request.form['login_key']
    owner = get_user_name(login_key)
    if owner:
        email = request.form['email']
        password = request.form['password']
        device_id = ''
        if 'device' in request.form:
            device_id = request.form['device']
        doc = User.create(email, password, device_id)
        return jsonify({'user': User.to_dict(doc)})
    else:
        abort(401)


@oiuser.route('', methods=['GET'])
@support_jsonp
@parse_args
def get_users(*args, **kwargs):
    resultset = []
    docs = User.get_all(*args, **kwargs)
    for doc in docs:
        resultset.append(User.to_safe_dict(doc))

    return jsonify({'resultset': resultset})


@oiuser.route('/login', methods=['POST'])
@crossdomain(origin='*')
def doLogin():
    user = request.form['email']
    pwd = request.form['password']
    user = User.authenticate(user, pwd)
    return jsonify(User.to_safe_dict(user)) if user else abort(401)

