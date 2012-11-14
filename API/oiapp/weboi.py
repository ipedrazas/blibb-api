#
#


from flask import Blueprint, request, abort, jsonify, current_app, g
from API.oiapp.models import Oi, Audit, User
from API.event.event import Event
from bson.objectid import ObjectId

from API.utils import get_user, is_valid_id
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
    owner = get_user(login_key)
    if owner:
        contacts = request.form['contacts']
        name = request.form['name']
        if 'tags' in request.form:
            tags = request.form['tags']
        current_app.logger.info(owner)
        doc = Oi.create(owner['username'], name, contacts, tags)
        if '_id' in doc:
            Audit.new_oi(owner, doc['_id'], '')
            return jsonify({'oi': Oi.to_dict(doc)})
        else:
            abort(409, doc.get('error','ERROR'))
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


@oi.route('/user/<user>', methods=['GET'])
@support_jsonp
@parse_args
def get_ois_by_user(user, *args, **kwargs):
    resultset = []
    senders = []
    subscribers = []
    invited = []

    docs = Oi.get_all({'$or': [{'owner': user.strip()}, {'senders': user.strip()}, {'subscribers':user.strip()}, {'invited': user.strip()}]}, **kwargs)
    for doc in docs:
        if 'senders' in doc and user in doc['senders']:
            senders.append(str(doc['_id']))
        if 'subscribers' in doc and user in doc['subscribers']:
            subscribers.append(str(doc['_id']))
        if 'invited' in doc and user in doc['invited']:
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
    user = get_user(login_key)
    if is_valid_id(oiid):
        oi = Oi.get({'_id': ObjectId(oiid)})
        if oi:
            if Oi.in_senders(oi, user):
                push = {'push': Oi.push(oi, user)}
                Audit.push(user['username'], oi['_id'], '', oi['subscribers'])
                return jsonify(push)
            else:
                abort(401)
        else:
            abort(404)
    abort(400)


@oi.route('/<oiid>/subscribe', methods=['POST'])
@crossdomain(origin='*')
def subscribe_oi(oiid=None):
    login_key = request.form['login_key']
    email = request.form['email']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if Oi.subscribe(oiid, user):
            if email is not None:
                User.add_subscrived_email(user, email)
            Audit.subscribe(user['username'], '', oiid)
            return jsonify({'subscribed': oiid})
        else:
            abort(401)
    abort(400)


@oi.route('/<oiid>/unsubscribe', methods=['POST'])
@crossdomain(origin='*')
def unsubscribe_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if Audit.unsubscribe(user['username'], '', oiid):
            return jsonify({'unsubscribed': oiid})
        else:
            abort(401)
    abort(400)


@oi.route('/<oiid>/history', methods=['GET'])
@support_jsonp
@parse_args
def get_history_oi(oiid, *args, **kwargs):
    resultset = []
    if is_valid_id(oiid):
        docs = Audit.get_all({'o': ObjectId(oiid)}, **kwargs)
        for doc in docs:
            resultset.append(Audit.to_dict(doc))
        return jsonify({'resultset': resultset})
    abort(400)