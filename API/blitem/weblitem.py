#
#


from flask import Blueprint, request, abort, jsonify, current_app, g
from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.event.event import Event


import API.utils as utils
from bson.objectid import ObjectId
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.error import Message

mod = Blueprint('blitem', __name__, url_prefix='/blitem')


@mod.before_request
def before_request():
    g.e = Event(request.path)


@mod.teardown_request
def teardown_request(exception):
    g.e.save()


####################
##### BLITEMS  #####
####################

@mod.route('', methods=['POST'])
@crossdomain(origin='*')
def newItem():
    bid = request.form['blibb_id']
    key = request.form['login_key']
    tags = request.form['tags']
    app_token = request.form['app_token']

    user = utils.get_user_name(key)
    current_app.logger.info('labels: ' + str(user))
    if utils.is_valid_id(bid):
        b = Blibb.get_object({'_id': ObjectId(bid)}, {'u': 1, 't.i.n': 1, 't.i.s': 1})
        if Blibb.can_write(user, app_token, bid):
            labels = Blibb.get_labels(b.get('t'))
            current_app.logger.info('labels: ' + str(labels))
            bitems = Blitem.get_items_from_request(labels, request)
            current_app.logger.info('items from request: ' + str(bitems))
            blitem_id = Blitem.insert(bid, user, bitems, tags)
            if blitem_id:
                cond = {'_id': ObjectId(bid)}
                Blibb.inc_num_item(cond)
            Blitem.post_process(blitem_id, bitems)
            return blitem_id
        else:
            abort(401)
    return jsonify(Message.get('id_not_valid'))


@mod.route('/fields/<blibb_id>', methods=['GET'])
@support_jsonp
def getBlitemFields(blibb_id=None):
    if utils.is_valid_id(blibb_id):
        b = Blibb.get_object({'_id': ObjectId(blibb_id)}, {'u': 1, 't.i.n': 1, 't.i.s': 1})
        res = Blibb.getLabels(b.get('t'))
    else:
        res = Message.get('id_not_valid')
    return jsonify(res)


@mod.route('/<blitem_id>', methods=['GET'])
@support_jsonp
def getBlitem(blitem_id=None):
    flat = request.args.get('flat')
    if flat:
        return jsonify(Blitem.get_item({'_id': ObjectId(blitem_id)}))
    else:
        return jsonify(Blitem.get_flat(blitem_id))
    abort(404)


@mod.route('/tag', methods=['POST'])
@crossdomain(origin='*')
def newTag():
    target_id = None
    key = request.form['k']
    user = utils.get_user_name(key)
    target_id = request.form['i']

    if Blitem.isOwner(target_id, user):
        tag = request.form['t']
        Blitem.addTag(target_id, tag)
    return jsonify({'response': 'ok'})


@mod.route('/<blibb_id>/items', methods=['GET'])
@support_jsonp
def getAllItemsFlat(blibb_id=None, page=1):
    r = Blitem.get_all_items(blibb_id, page)
    if r != 'null':
        return jsonify(r)
    else:
        abort(404)


@mod.route('/<blibb_id>/v/<view>', methods=['GET'])
@support_jsonp
def getItemsByBlibbAndView(blibb_id=None, view='Default'):
    # This method returns all the blitems
    # by blibb and rendered with the view
    # passed
    b = Blibb()
    r = b.getTemplateView(blibb_id, view)
    if r != 'null':
        return r
    else:
        abort(404)
