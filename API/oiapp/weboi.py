#
#


from flask import Blueprint, request, abort, jsonify, current_app, g
from API.oiapp.models import Oi
from API.event.event import Event
from bson.objectid import ObjectId

from API.utils import get_email, is_valid_id
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.decorators import parse_args


oi = Blueprint('oi', __name__, url_prefix='/ois')


@oi.before_request
def before_request():
    g.e = Event(request.path)


@oi.teardown_request
def teardown_request(exception):
    g.e.save()


@oi.route('', methods=['POST'])
@crossdomain(origin='*')
def new_oi():
    login_key = request.form['login_key']
    owner = get_email(login_key)
    if owner:
        contacts = request.form['contacts']
        name = request.form['name']
        current_app.logger.info(owner)
        doc = Oi.create(owner, name, contacts)
        return jsonify({'oi': Oi.to_dict(doc)})
    else:
        abort(401)


@oi.route('', methods=['GET'])
@support_jsonp
@parse_args
def get_ois(*args, **kwargs):
    resultset = []
    docs = Oi.get_all(*args, **kwargs)
    for doc in docs:
        resultset.append(Oi.to_dict(doc))

    return jsonify({'resultset': resultset})


@oi.route('/<email>', methods=['GET'])
@support_jsonp
@parse_args
def get_ois_by_user(email, *args, **kwargs):
    resultset = []
    docs = Oi.get_all({'$or': [{'senders': email.strip()}, {'subscribers':email.strip()}, {'subscribers': email.strip()}]}, **kwargs)
    for doc in docs:
        resultset.append(Oi.to_dict(doc))

    return jsonify({'resultset': resultset})


@oi.route('/<oiid>', methods=['GET'])
@support_jsonp
def get_oi(oiid):
    if is_valid_id(oiid):
        doc = Oi.get({'_id': ObjectId(oiid)})
        return jsonify({'oi': Oi.to_dict(doc)})
    abort(400)


@oi.route('/<oiid>/push', methods=['POST'])
@crossdomain(origin='*')
def push_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_email(login_key)
    if is_valid_id(oiid):
        if Oi.can_push(oiid, user):
            return jsonify({'push': Oi.push(oiid)})
        else:
            abort(401)
    abort(400)


@oi.route('/<oiid>/subscribe', methods=['POST'])
@crossdomain(origin='*')
def subscribe_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_email(login_key)
    if is_valid_id(oiid):
        if Oi.subscribe(oiid, user):
            return jsonify({'subscribed': oiid})
        else:
            abort(401)
    abort(400)
