

import json
from flask import Blueprint, request, abort, jsonify
from API.blibb.blibb import Blibb
from API.event.event import Event
from API.contenttypes.picture import Picture
from API.user.buser import User
import API.utils as utils
from bson.objectid import ObjectId

from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('blibb', __name__, url_prefix='/blibb')


@mod.route('/meta/webhooks/<bid>', methods=['GET'])
def getWebhooks(bid=None):
    if utils.is_valid_id(bid):
        b = Blibb()
        fields = b.getWebhooks(bid)
        return jsonify({'webhooks': fields})
    else:
        return jsonify({'error': 'Object id not valid'})


@mod.route('/meta/fields/<bid>', methods=['GET'])
def getBlibbFields(bid=None):
    if bid is not None:
        fields = Blibb.get_fields(bid)
        return jsonify({'fields': fields})


@mod.route('', methods=['POST'])
def newBlibb():
    e = Event('web.blibb.newBlibb')
    name = request.form['bname']
    desc = request.form['bdesc']
    template = request.form['btemplate']
    key = request.form['bkey']
    user = utils.get_user_name(key)
    image_id = request.form['bimage']
    slug = request.form['slug']
    write_access = request.form['write_access']
    read_access = request.form['read_access']

    # check if a blibb with that slug already exists
    blibb = Blibb.get_by_slug(user, slug)
    # return jsonify(blibb)

    if not blibb:
        res = {'error': 'None'}
        if utils.is_valid_id(image_id):
            image = Picture.dump_image(image_id)
        else:
            image = 'blibb.png'

        new_id = Blibb.insert(user, name, slug, desc, template, image, read_access, write_access)
        res = {'id': new_id}
    else:
        res = {'error': 'Blibb with that slug already exists'}

    e.save()
    return jsonify(res)


@mod.route('/<blibb_id>/p/<params>', methods=['GET'])
@crossdomain(origin='*')
def getBlibb(blibb_id=None, params=None):
    e = Event('web.blibb.getBlibb')
    if blibb_id is None:
        abort(404)

    if params is None:
        r = Blibb.get_by_id(blibb_id)
    else:
        r = Blibb.get_by_id_params(blibb_id, params)

    e.save()
    if r != 'null':
        return jsonify(r)
    else:
        abort(404)


@mod.route('/<blibb_id>/template', methods=['GET'])
@crossdomain(origin='*')
def getBlibbTemplate(blibb_id=None):
    e = Event('web.blibb.getBlibbTemplate')
    b = Blibb()
    r = b.get_template(blibb_id)
    e.save()
    if r != 'null':
        return r
    else:
        abort(404)


@mod.route('/<blibb_id>/view', methods=['GET'])
@mod.route('/<blibb_id>/view/<view_name>', methods=['GET'])
def getBlibbView(blibb_id=None, view_name='null'):
    e = Event('web.blibb.getBlibbView')
    if utils.is_valid_id(blibb_id):
        r = Blibb.getTemplateView(blibb_id, view_name)
        e.save()
        if r != 'null':
            return jsonify(r)
        else:
            abort(404)
    else:
        abort(400)


@mod.route('/<username>', methods=['GET'])
@support_jsonp
def getBlibbByUser(username=None):
    e = Event('web.blibb.getBlibbByUser')
    b = Blibb()
    if username is None:
        abort(404)
    res = b.get_by_user(username)
    e.save()
    return jsonify(res)


@mod.route('/<username>/group', methods=['GET'])
def getGroupBlibbByUser(username=None):
    e = Event('web.blibb.getGroupBlibbByUser')
    b = Blibb()
    if username is None:
        abort(404)
    res = b.getByGroupUser(username)
    e.save()
    return res


#####################
####### TAGS  #######
#####################

@mod.route('/tag', methods=['POST'])
def newTag():
    e = Event('web.blibb.newTag')
    target_id = None
    target = None
    key = request.form['k']
    user = utils.get_user_name(key)
    target_id = request.form['b']
    if Blibb.can_write(target_id, user):
        tag = request.form['t']
        target.addTag(target_id, tag)

    e.save()
    return json.dumps('ok')


@mod.route('/del', methods=['POST'])
def deleteBlibb():
    e = Event('web.blibb.deleteBlibb')
    key = request.form['login_key']
    bid = request.form['blibb_id']
    user = utils.get_user_name(key)
    if utils.is_valid_id(bid):
        filter = {'_id': ObjectId(bid), 'u': user}
        Blibb.remove(filter)
    e.save()
    return jsonify({'ret': 1})


@mod.route('/action/image', methods=['POST'])
@crossdomain(origin='*')
def updateImage():
    e = Event('web.blibb.updateImage')
    object_id = request.form['object_id']
    image_id = request.form['image_id']
    if object_id is None:
        abort(404)
    if utils.is_valid_id(image_id) and utils.is_valid_id(object_id):
        Blibb.add_picture({'_id': ObjectId(object_id)}, image_id)
    e.save()
    return 'ok'


@mod.route('/actions/webhook', methods=['POST'])
@crossdomain(origin='*')
def add_webhook():
    e = Event('web.blibb.add_webhook')
    key = request.form['login_key']
    bid = request.form['blibb_id']
    callback = request.form['callback']
    fields = request.form['fields']
    action = request.form['action']
    user = utils.getKey(key)
    res = dict()
    wb = {'a': action, 'u': callback, 'f': fields}
    if utils.is_valid_id(bid):
        if Blibb.can_write(bid, user):
            Blibb.add_webhook(bid, wb)
            res['result'] = 'ok'
        else:
            abort(401)
    else:
        res['error'] = 'Object Id is not valid'
    e.save()
    return jsonify(res)


@mod.route('/actions/group', methods=['POST'])
@crossdomain(origin='*')
def add_user_to_group():
    e = Event('web.blibb.add_user_to_group')
    key = request.form['login_key']
    bid = request.form['blibb_id']
    username = request.form['username']
    user = utils.getKey(key)
    res = dict()
    if utils.is_valid_id(bid):
        user_to_add = User.get_by_name(username)
        if user_to_add:
            if Blibb.can_write(user, bid):
                Blibb.add_user_to_group(username, bid)
                res['result'] = 'ok'
            else:
                res['error'] = 'Not permissions'
        else:
            res['error'] = 'User not found'
    else:
        res['error'] = 'Object Id is not valid'
    e.save()
    return jsonify(res)
