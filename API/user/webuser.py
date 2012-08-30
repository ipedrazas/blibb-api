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
from API.comment.comment import Comment
from API.utils import is_valid_id, get_key
from bson.objectid import ObjectId
from flask import Blueprint, request, abort, current_app, jsonify, make_response, g
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.user.blibb2rss import blibb2rss
import json
from API.error import Message

# from blinker import signal


# def do_login(user):
#     print 'signal:' + str(user)
#     e = Event('signal.login')
#     e.addLog(user)
#     e.save()


# is_login = signal('event')
# is_login.connect(do_login)


mod = Blueprint('user', __name__, url_prefix='')


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

#####################
###### USERS  #######
#####################


@mod.route('/user/<key>', methods=['GET'])
@support_jsonp
@crossdomain(origin='*')
def getUserByName(key=None):
    if key is None:
        abort(404)
    u = User.get_by_name(key)
    if u:
        return jsonify({'user': u})
    else:
        user = User.get_user(key)
        return jsonify({'user': json.loads(user)})


@mod.route('/logout', methods=['POST'])
@crossdomain(origin='*')
def doLogout():
    login_key = request.form['login_key']
    r = User.get_redis()
    r.delete(login_key)
    return jsonify({'res': User.logout(login_key)})


@mod.route('/login', methods=['POST'])
@crossdomain(origin='*')
def doLogin():
    user = request.form['u']
    pwd = request.form['p']
    user = User.authenticate(user, pwd)
    return jsonify(user) if user else abort(401)


@mod.route('/<username>/<slug>', methods=['DELETE'])
@crossdomain(origin='*')
@support_jsonp
def deleteBlibb(username=None, slug=None):
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


@mod.route('/<username>/<slug>/<item_id>', methods=['DELETE'])
@crossdomain(origin='*')
@support_jsonp
def deleteItem(username=None, slug=None, item_id=None):
    if username is None or slug is None or item_id is None:
        abort(404)


@mod.route('/<username>/<slug>', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@support_jsonp
def addItemtoBlibb(username=None, slug=None):
    if username is None or slug is None:
        abort(404)

    user = ''
    app_token = ''
    if 'login_key' in request.form:
        key = request.form['login_key']
        user = get_key(key)
    else:
        app_token = request.form['app_token'] if 'app_token' in request.form else ''

    tags = request.form['tags'] if 'tags' in request.form else ''
    blibb = Blibb.get_object({'u': username, 's': slug}, {'_id': 1})
    blibb_id = blibb['_id']
    current_app.logger.info(str(user) + ' - ' + str(app_token) + ' - ' + str(blibb_id) + ' - ' + username + ' - ' + slug)
    if Blibb.can_write(user, app_token, blibb_id):
        labels = Blibb.get_label_from_template(blibb_id)
        bitems = Blitem.get_items_from_request(labels, request)
        blitem_id = Blitem.insert(blibb_id, user, bitems, tags)
        if is_valid_id(blitem_id):
            cond = {'s': slug, 'u': username}
            Blibb.inc_num_item(cond)
            Blitem.post_process(blitem_id, bitems)
            res = {'id': blitem_id}
            return jsonify(res)
    else:
        abort(401)


@mod.route('/<username>/<slug>', methods=['GET'])
@crossdomain(origin='*')
@support_jsonp
def get_blibb_by_slug(username=None, slug=None):
    attributes = {'tags': True}
    url = request.url
    ret = get_by_slug(username, slug, url, attributes, True)
    return  jsonify(ret)


@mod.route('/<username>/<slug>.xml', methods=['GET'])
@support_jsonp
@crossdomain(origin='*')
def get_as_rss(username=None, slug=None):
    if username is None or slug is None:
        return None
    url = request.url
    ret = get_by_slug(username, slug, url, {}, False)
    rss = blibb2rss(ret)
    response = make_response(str(rss.output()))
    response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
    current_app.logger.info(str(ret))
    return response


def get_by_slug(username=None, slug=None, url=None, attributes={}, flat=True):
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
    return ret


@mod.route('/user/image', methods=['POST'])
@crossdomain(origin='*')
def setImageUser():
    user_id = request.form['user_id']
    image_url = request.form['image_url']
    if is_valid_id(user_id):
        User.add_picture({'_id': ObjectId(user_id)}, image_url)
        return jsonify({'response': 'ok'})
    return abort(404)


@mod.route('/user', methods=['POST'])
@crossdomain(origin='*')
def newUser():
    user = request.form['user']
    pwd = request.form['pwd']
    code = request.form['code']
    email = request.form['email']
    m = Manager()
    res = dict()
    if m.validateCode(code):
        u_id = User.create(user, email, pwd, code)
        if u_id:
            res = {'id': u_id}
        else:
            res = {'error': 'Username/email is already in use'}
    else:
        res = {'error': 'Code is not valid'}
    return jsonify(res)


@mod.route('/<username>/<slug>/tag/<tag>', methods=['GET'])
@crossdomain(origin='*')
@support_jsonp
def get_items_by_tag(username=None, slug=None, tag=None):
    if username is None or slug is None or tag is None:
        abort(404)
    # ip = request.remote_addr
    blibb_id = Blibb.get_id_by_slug(username, slug)
    cond = {'s': slug, 'u': username}
    Blibb.increase_view(cond, 'vt')
    # return blibb_id
    b = Blitem()
    items = b.getItemsByTag(blibb_id, tag)
    return  jsonify(items)


@mod.route('/<username>/<slug>/<id>', methods=['GET'])
@crossdomain(origin='*')
@support_jsonp
def get_item_by_id(username=None, slug=None, id=None):
    if username is None or  slug is None or id is None:
        abort(404)

    blibb = Blibb.get_object({'u': username, 's': slug})
    if blibb and is_valid_id(id):
        blibb_id = blibb['_id']
        items = Blitem.get_item({'_id': ObjectId(id), 'b': ObjectId(blibb_id)})
        return  jsonify(Blitem.flat_object(items, {}))
    else:
        return jsonify(Message.get('id_not_valid'))


@mod.route('/<username>/<slug>/comment/<item_id>', methods=['GET'])
@support_jsonp
@crossdomain(origin='*')
def getComments(username=None, slug=None, item_id=None):
    if is_valid_id(item_id):
        cs = Comment.get_comments_by_id(item_id)
        return jsonify({'comments': cs})
    abort(404)

