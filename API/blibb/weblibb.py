

import json
from flask import Blueprint, request, abort, jsonify, g, current_app
from API.blibb.blibb import Blibb
from API.event.event import Event
from API.contenttypes.picture import Picture
from API.user.buser import User
from API.utils import is_valid_id, get_user_name, get_key
from bson.objectid import ObjectId

from API.decorators import crossdomain, support_jsonp


mod = Blueprint('blibb', __name__, url_prefix='/blibb')


@mod.route('/favicon.ico')
@mod.route('/robots.txt')
@mod.route('/index.html')
@mod.route('/scripts/<path:any>')
def handle(any=None):
    abort(404)


@mod.before_request
def before_request():
    g.e = Event(request.path)


@mod.teardown_request
def teardown_request(exception):
    g.e.save()

#
#   /blibb [POST, DELETE]
#


@mod.route('', methods=['POST'])
@crossdomain(origin='*')
def newBlibb():
    name = request.form['bname']
    desc = request.form['bdesc']
    template = request.form['btemplate']
    key = request.form['bkey']
    user = get_user_name(key)
    image_id = request.form['bimage']
    slug = request.form['slug']
    write_access = request.form['write_access']
    read_access = request.form['read_access']

    # check if a blibb with that slug already exists
    blibb = Blibb.get_by_slug(user, slug)
    # return jsonify(blibb)

    if not blibb:
        res = {'error': 'None'}
        if is_valid_id(image_id):
            image = Picture.dump_image(image_id)
        else:
            image = 'blibb.png'

        new_id = Blibb.insert(user, name, slug, desc, template, image, read_access, write_access)
        res = {'id': new_id}
    else:
        res = {'error': 'Blibb with that slug already exists'}
    return jsonify(res)


@mod.route('/view', methods=['PUT'])
@crossdomain(origin='*')
def updateView():
    blibb_id = request.form['blibb_id']
    user = get_user_name(request.form['login_key'])
    view = request.form['viewName']
    html = request.form['viewHtml']
    # current_app.logger.info(user + ' ' + blibb_id + ' ' + view + ' ' + html)
    if is_valid_id(blibb_id):
        if Blibb.can_write(user, '', blibb_id):
            Blibb.update_view(blibb_id, user, view, html)
            return jsonify({'result': 'View Updated'})
        else:
            abort(401)
    abort(404)


@mod.route('/<blibb_id>/<login_key>', methods=['DELETE'])
@crossdomain(origin='*')
def deleteBlibb(blibb_id=None, login_key=None):
    user = get_user_name(login_key)
    if is_valid_id(blibb_id):
        filter = {'_id': ObjectId(blibb_id), 'u': user}
        Blibb.remove(filter)
    return jsonify({'ret': 1})


@mod.route('/<blibb_id>/p/<params>', methods=['GET'])
@crossdomain(origin='*')
def getBlibb(blibb_id=None, params=None):
    if blibb_id is None:
        abort(404)

    if params is None:
        o = Blibb.get_object(blibb_id)
        r = Blibb.flat_object(o)
    else:
        r = Blibb.get_by_id_params(blibb_id, params)

    if r != 'null':
        return jsonify(r)
    else:
        abort(404)

@mod.route('/short/<short_id>', methods=['GET'])
@crossdomain(origin='*')
def getBlibbShort(short_id=None, params=None):
    if short_id is None:
        abort(404)

    if params is None:
        o = Blibb.get_object({'si': short_id})
        r = Blibb.flat_object(o)

    if r != 'null':
        return jsonify(r)
    else:
        abort(404)


@mod.route('/<blibb_id>/template', methods=['GET'])
@crossdomain(origin='*')
def getBlibbTemplate(blibb_id=None):
    b = Blibb()
    r = b.get_template(blibb_id)
    if r != 'null':
        return r
    else:
        abort(404)


@mod.route('/<blibb_id>/view', methods=['GET'])
@crossdomain(origin='*')
def getBlibbView(blibb_id=None, view_name='null'):
    if is_valid_id(blibb_id):
        r = Blibb.get_template_view(blibb_id)
        if r != 'null':
            return jsonify(r)
        else:
            abort(404)
    else:
        abort(400)


@mod.route('/<username>', methods=['GET'])
@crossdomain(origin='*')
@support_jsonp
def getBlibbByUser(username=None):
    b = Blibb()
    if username is None:
        abort(404)
    res = b.get_by_user(username)
    return jsonify(res)


@mod.route('/<username>/group', methods=['GET'])
@crossdomain(origin='*')
def getGroupBlibbByUser(username=None):
    b = Blibb()
    if username is None:
        abort(404)
    res = b.getByGroupUser(username)
    return res


@mod.route('/fork', methods=['POST'])
@crossdomain(origin='*')
def fork():
    key = request.form['login_key']
    user = get_user_name(key)
    target_id = request.form['b']
    Blibb.fork(target_id, user)
    return json.dumps('ok')


#####################
####### TAGS  #######
#####################

@mod.route('/tag', methods=['POST'])
@crossdomain(origin='*')
def newTag():
    target_id = None
    target = None
    key = request.form['k']
    user = get_user_name(key)
    target_id = request.form['b']
    if Blibb.can_write(target_id, user):
        tag = request.form['t']
        target.addTag(target_id, tag)

    return json.dumps('ok')


@mod.route('/action/image', methods=['POST'])
@crossdomain(origin='*')
def updateImage():
    object_id = request.form['object_id']
    image_id = request.form['image_id']
    if object_id is None:
        abort(404)
    if is_valid_id(image_id) and is_valid_id(object_id):
        Blibb.add_picture({'_id': ObjectId(object_id)}, image_id)
    return 'ok'


@mod.route('/actions/webhook', methods=['POST'])
@crossdomain(origin='*')
def add_webhook():
    key = request.form['login_key']
    bid = request.form['blibb_id']
    callback = request.form['callback']
    fields = request.form['fields']
    action = request.form['action']
    user = get_key(key)
    res = dict()
    wb = {'a': action, 'u': callback, 'f': fields}
    if is_valid_id(bid):
        if Blibb.can_write(user, '', bid):
            Blibb.add_webhook(bid, wb)
            res['result'] = 'ok'
        else:
            abort(401)
    else:
        res['error'] = 'Object Id is not valid'
    return jsonify(res)


@mod.route('/actions/group', methods=['POST'])
@crossdomain(origin='*')
def add_user_to_group():
    key = request.form['login_key']
    bid = request.form['blibb_id']
    username = request.form['username']
    user = get_key(key)
    res = dict()
    if is_valid_id(bid):
        user_to_add = User.get_by_name(username)
        if user_to_add:
            if Blibb.can_write(user, '', bid):
                Blibb.add_user_to_group(username, bid)
                res['result'] = 'ok'
            else:
                res['error'] = 'Not permissions'
        else:
            res['error'] = 'User not found'
    else:
        res['error'] = 'Object Id is not valid'
    return jsonify(res)


@mod.route('/meta/webhooks/<bid>', methods=['GET'])
@crossdomain(origin='*')
def getWebhooks(bid=None):
    if is_valid_id(bid):
        b = Blibb()
        fields = b.getWebhooks(bid)
        return jsonify({'webhooks': fields})
    else:
        return jsonify({'error': 'Object id not valid'})


@mod.route('/meta/fields/<bid>', methods=['GET'])
@crossdomain(origin='*')
def getBlibbFields(bid=None):
    if bid is not None:
        fields = Blibb.get_fields(bid)
        return jsonify({'fields': fields})


@mod.route('/object/<bid>', methods=['GET'])
@crossdomain(origin='*')
def getObject(bid=None):
    if bid is not None:
        params = request.args.get('fields')
        fields = dict()
        for p in params.split(','):
            fields[p] = 1
        current_app.logger.info(fields)
        doc = Blibb.get_object({'_id': ObjectId(bid)}, fields)
        blibb = Blibb.to_dict(doc)
        #
        return jsonify(Blibb.flat_object(blibb))
    abort(404)
