#
#


from flask import Blueprint, request, abort, jsonify, current_app, g
from API.oiapp.models import Oi, Audit
from API.event.event import Event
from bson.objectid import ObjectId

from API.utils import get_email, is_valid_id, queue_ducksboard_delta
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
        Audit.new_oi(owner, doc['_id'], '')
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
    senders = []
    subscribers = []
    invited = []

    docs = Oi.get_all({'$or': [{'senders': email.strip()}, {'subscribers':email.strip()}, {'invited': email.strip()}]}, **kwargs)
    for doc in docs:
        if email in doc['senders']:
            senders.append(str(doc['_id']))
        if email in doc['subscribers']:
            subscribers.append(str(doc['_id']))
        if email in doc['invited']:
            invited.append(str(doc['_id']))
        resultset.append(Oi.to_dict(doc))
    data = {'senders': senders, 'subscribers': subscribers, 'invited': invited}
    return jsonify({'resultset': resultset, 'data': data})


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
        oi = Oi.get({'_id': ObjectId(oiid)})
        if Oi.in_senders(oi, user):
            Audit.push(user, oi['_id'], '', oi['subscribers'])
            return jsonify({'push': Oi.push(oi)})
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
            Audit.subscribe(user, '', oiid)
            return jsonify({'subscribed': oiid})
        else:
            abort(401)
    abort(400)
