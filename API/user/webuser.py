#
#
#
#
#
#
#

from API.om.manager import Manager
from API.user.buser import User
from API.blibb.blibb import Blibb
from API.blitem.blitem import Blitem
from API.event.event import Event
from API.utils import is_valid_id, get_key
from bson.objectid import ObjectId
from flask import Blueprint, request, abort, current_app, jsonify, make_response
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.user.blibb2rss import blibb2rss

from API.error import Message

mod = Blueprint('user', __name__, url_prefix='')


@mod.route('/favicon.ico')
@mod.route('/robots.txt')
@mod.route('/index.html')
@mod.route('/scripts/<path:any>')
def handle(any=None):
    abort(404)


#####################
###### USERS  #######
#####################


@mod.route('/<username>/<slug>', methods=['DELETE'])
@crossdomain(origin='*')
@support_jsonp
def deleteBlibb(username=None, slug=None):
    e = Event('web.user.blibb.deleteItem')
    if username is None or slug is None:
        abort(404)
    b = Blibb()
    dres = b.getBySlug(username, slug)
    results = dres.get('results', '')
    count = dres.get('count', 0)
    if count > 0:
        jblibb = results[0]
        bid = jblibb['id']
        filter = {'_id': ObjectId(bid)}
        b.remove(filter)

    e.save()


@mod.route('/<username>/<slug>/<item_id>', methods=['DELETE'])
@crossdomain(origin='*')
@support_jsonp
def deleteItem(username=None, slug=None, item_id=None):
    e = Event('web.user.blibb.deleteItem')
    if username is None or slug is None or item_id is None:
        abort(404)

    e.save()


@mod.route('/<username>/<slug>', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@support_jsonp
def addItemtoBlibb(username=None, slug=None):
    e = Event('web.user.blibb.getBlibbBySlug')
    if username is None or slug is None:
        abort(404)
    app_token = request.form['app_token'] if 'app_token' in request.form else ''
    key = request.form['login_key'] if 'login_key' in request.form else ''
    e.addLog({'at': app_token})
    e.addLog({'s': slug})

    tags = request.form['tags'] if 'tags' in request.form else ''
    user = get_key(key)
    blibb_id = Blibb.get_id_by_slug(username, slug)

    if Blibb.can_write(user, app_token, blibb_id):
        e.addLog({'b': blibb_id})
        labels = Blibb.get_label_from_template(blibb_id)
        bitems = Blitem.get_items_from_request(labels, request)
        blitem_id = Blitem.insert(blibb_id, user, bitems, tags)

        if is_valid_id(blitem_id):
            cond = {'s': slug, 'u': username}
            Blibb.inc_num_item(cond)
            Blitem.post_process(blitem_id, bitems)
            res = {'id': blitem_id}
            e.save()
            return jsonify(res)
    else:
        e.save()
        abort(401)


@mod.route('/<username>/<slug>', methods=['GET'])
@support_jsonp
def get_blibb_by_slug(username=None, slug=None):
    e = Event('web.user.blibb.get_blibb_by_slug')
    attributes = {'tags': True}
    url = request.url
    ret = get_by_slug(username, slug, url, attributes, True)
    e.save()
    return  jsonify(ret)


@mod.route('/<username>/<slug>.xml', methods=['GET'])
@support_jsonp
def get_as_rss(username=None, slug=None):
    e = Event('web.user.blibb.get_by_slug')
    if username is None or slug is None:
        return None
    url = request.url
    ret = get_by_slug(username, slug, url, {}, False)
    rss = blibb2rss(ret)
    response = make_response(str(rss.output()))
    response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
    current_app.logger.info(str(ret))
    e.save()
    return response


def get_by_slug(username=None, slug=None, url=None, attributes={}, flat=True):
    e = Event('web.user.blibb.get_by_slug')
    if username is None or slug is None:
        return None

    page = request.args.get('page', 1)
    # comments = request.args.get('comments', 0)
    blibb = Blibb.get_by_slug(username, slug)
    if url:
        blibb['url'] = url
    ret = dict()
    cond = {'s': slug, 'u': username}
    Blibb.increase_view(cond, 'v')
    ret['blibb'] = blibb
    rs_items = Blitem.get_all_items(blibb['id'], int(page), attributes, flat)
    ret['items'] = rs_items['items']
    e.save()
    return ret


@mod.route('/user/name/<user_name>', methods=['GET'])
@support_jsonp
def getUserByName(user_name=None):
    e = Event('web.user.getUserByName')
    if user_name is None:
        abort(404)
    u = User.get_by_name(user_name)
    e.save()
    return jsonify(u)


@mod.route('/user/image', methods=['POST'])
@crossdomain(origin='*')
def setImageUser():
    e = Event('web.user.setImageUser')
    user_id = request.form['object_id']
    image_id = request.form['image_id']
    if user_id is None:
        abort(404)
    if is_valid_id(user_id):
        User.add_picture({'_id': ObjectId(user_id)}, image_id)
    e.save()
    return 'ok'


@mod.route('/login', methods=['POST'])
@crossdomain(origin='*')
def doLogin():
    e = Event('web.user.doLogin')
    user = request.form['u']
    pwd = request.form['p']
    user = User.authenticate(user, pwd)
    if user:
        e.save()
        return jsonify(user)
    else:
        e.save()
        abort(401)


@mod.route('/user', methods=['POST'])
@crossdomain(origin='*')
def newUser():
    e = Event('web.user.newUser')
    user = request.form['user']
    pwd = request.form['pwd']
    code = request.form['code']
    email = request.form['email']

    m = Manager()
    if m.validateCode(code):
        u_id = User.create(user, email, pwd, code)
        e.save()
        return jsonify({'id': u_id})
    else:
        e.save()
        return jsonify({'error': 'Code is not valid'})


@mod.route('/<username>/<slug>/tag/<tag>', methods=['GET'])
@support_jsonp
def get_items_by_tag(username=None, slug=None, tag=None):
    e = Event('web.user.blibb.get_items_by_tag')

    if username is None:
        abort(404)
    if slug is None:
        abort(404)
    if tag is None:
        abort(404)

    ip = request.remote_addr
    e.addLog(ip)

    blibb_id = Blibb.get_id_by_slug(username, slug)
    cond = {'s': slug, 'u': username}
    Blibb.increase_view(cond, 'vt')

    # return blibb_id
    b = Blitem()
    items = b.getItemsByTag(blibb_id, tag)
    e.save()
    return  jsonify(items)


@mod.route('/<username>/<slug>/<id>', methods=['GET'])
@support_jsonp
def get_item_by_id(username=None, slug=None, id=None):
    e = Event('web.user.blibb.get_item_by_id')
    if username is None or  slug is None or id is None:
        abort(404)

    blibb_id = Blibb.get_id_by_slug(username, slug)
    if is_valid_id(id) and is_valid_id(blibb_id):
            items = Blitem.get_item({'_id': ObjectId(id), 'b': ObjectId(blibb_id)})
            e.save()
            return  jsonify(Blitem.flat_object(items, {}))
    else:
        return jsonify(Message.get('id_not_valid'))
