#
#


from flask import Blueprint, request, abort, jsonify, current_app, g, render_template
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


@oi.errorhandler(401)
@crossdomain(origin='*')
def custom_401(error):
     return render_template('401.html'), 401

@oi.route('', methods=['POST'])
@crossdomain(origin='*')
def new_oi():
    login_key = request.form['login_key']
    owner = get_user(login_key)
    if owner:
        contacts = request.form['contacts']
        name = request.form['name']
        comments = request.form['comments']
        tags = request.form['tags']
        gp = int(request.form.get('group', 0))
        group = True if gp == 1 else False
        pub = int(request.form.get('public', 0))
        public = True if pub == 1 else False

        doc = Oi.create(owner['username'], name, contacts, tags, comments, group, public)
        if '_id' in doc:
            Audit.new_oi(owner['username'], doc['_id'], '')
            return jsonify({'oi': Oi.to_dict(doc)})
        else:
            abort(409, doc.get('error','ERROR'))
    else:
        abort(401)


@oi.route('', methods=['PATCH'])
@crossdomain(origin='*')
def update_oi():
    login_key = request.form['login_key']
    attr_name  = request.form['attr_name']
    attr_value = request.form['attr_value']
    oiid = request.form['oiid']
    owner = get_user(login_key)
    if owner:
        Oi.update(oiid, {attr_name: attr_value})
        return jsonify({'result': {'code': 1, 'msg': 'Object updated'}})
    abort(401)


@oi.route('', methods=['GET'])
@support_jsonp
@parse_args
def get_ois(*args, **kwargs):
    resultset = []
    docs = Oi.get_all({'del': {'$exists': False}}, **kwargs)
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

    docs = Oi.get_all(
                        {'$and': [
                            {'del': {'$exists': False}},
                            {'$or': [
                                {'owner': user.strip()},
                                {'senders': user.strip()},
                                {'subscribers':user.strip()},
                                {'invited': user.strip()}
                            ]}
                        ]},
                         **kwargs)

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
        doc = Oi.get({'_id': ObjectId(oiid), 'del': {'$exists': False}})
        return jsonify({'oi': Oi.to_dict(doc)})
    abort(400)

@oi.route('/user/<username>/public', methods=['GET'])
@support_jsonp
@parse_args
def get_public_oi(username, *args, **kwargs):
    resultset = []
    docs = Oi.get_all({'del': {'$exists': False},'owner': username, 'public': True}, **kwargs)
    for doc in docs:
        resultset.append(Oi.to_dict(doc))
    return jsonify({'resultset': resultset})



@oi.route('/<oiid>/push', methods=['POST'])
@crossdomain(origin='*')
def push_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_user(login_key)
    if is_valid_id(oiid):
        oi = Oi.get({'_id': ObjectId(oiid), 'del': {'$exists': False}})
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

# it should be DELETE... but it doesn't work..
@oi.route('/<oiid>/del', methods=['POST'])
@crossdomain(origin='*')
def delete_oi(oiid=None):
    login_key = request.form['login_key']
    if is_valid_id(oiid):
        doc = Oi.get({'_id': ObjectId(oiid), 'del': {'$exists': False}})
        if doc:
            owner = get_user(login_key)
            current_app.logger.info(str(owner))
            current_app.logger.info(str(doc))
            if owner['username'] == doc['owner']:
                Oi.update(oiid, {'name':'del', 'value': True})
                Audit.delete(owner['username'],'',oiid)
                return jsonify({'result': {'code': 'true', 'msg': 'Object deleted'}})
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
            return jsonify({'result': {'code': 'true', 'msg': 'Object subscribed'}})
        else:
            abort(401)
    abort(400)

@oi.route('/<oiid>/reject', methods=['POST'])
@crossdomain(origin='*')
def reject_oi(oiid=None):
    login_key = request.form['login_key']
    email = request.form['email']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if Oi.reject(oiid, email):
            Audit.reject(user['username'], '', oiid)
            return jsonify({'result': {'code': 'true', 'msg': 'Object rejected'}})
        else:
            abort(401)
    abort(400)


@oi.route('/<oiid>/unsubscribe', methods=['POST'])
@crossdomain(origin='*')
def unsubscribe_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if user:
            if Oi.unsubscribe(oiid, user['username']):
                Audit.unsubscribe(user['username'], '', oiid)
                return jsonify({'result': {'code': 'true', 'msg': 'Object unsubscribed'}})
        abort(401)
    abort(400)

@oi.route('/<oiid>/<username>/unsubscribe', methods=['POST'])
@crossdomain(origin='*')
def unsubscribe_oi(oiid=None, username=None):
    login_key = request.form['login_key']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if Oi.unsubscribe_user(oiid, user, username):
            Audit.unsubscribe(username, '', oiid)
            return jsonify({'result': {'code': 'true', 'msg': 'Object unsubscribed'}})
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
    else:
        docs = Audit.get_all({'u': oiid}, **kwargs)
        for doc in docs:
            resultset.append(Audit.to_dict(doc))
        return jsonify({'resultset': resultset})
    abort(400)


@oi.route('/<oiid>/invited', methods=['POST'])
@crossdomain(origin='*')
def add_invited_oi(oiid=None):
    login_key = request.form['login_key']
    invited = request.form['email']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if user
            if Oi.add_invitation(oiid, invited):
                return jsonify({'result': {'code': 'true', 'msg': 'Object fav'}})
        abort(401)
    abort(400)


@oi.route('/<oiid>/fav', methods=['POST'])
@crossdomain(origin='*')
def fav_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if user:
            if Oi.fav(oiid, user['username']):
                Audit.fav(user['username'], '', oiid)
                return jsonify({'result': {'code': 'true', 'msg': 'Object fav'}})
        abort(401)
    abort(400)


@oi.route('/<oiid>/unfav', methods=['POST'])
@crossdomain(origin='*')
def unfav_oi(oiid=None):
    login_key = request.form['login_key']
    user = get_user(login_key)
    if is_valid_id(oiid):
        if user:
            if Oi.unfav(oiid, user['username']):
                Audit.unfav(user['username'], '', oiid)
                return jsonify({'result': {'code': 'true', 'msg': 'Object unfav'}})
        abort(401)
    abort(400)
