

from flask import Blueprint, request, current_app, jsonify, abort, g
from API.comment.comment import Comment
from API.event.event import Event
from API.blitem.blitem import Blitem
from API.utils import get_user_name, is_valid_id

from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('comment', __name__, url_prefix='/comment')


@mod.before_request
def before_request():
    g.e = Event(request.path)


@mod.teardown_request
def teardown_request(exception):
    g.e.save()


#####################
##### COMMENTS  #####
#####################


@mod.route('', methods=['POST'])
@crossdomain(origin='*')
def newComment():
    key = request.form['login_key']
    target_id = request.form['item_id']
    text = request.form['comment']
    user = get_user_name(key)
    if user is not None:
        c_id = Comment.insert(target_id, user, text)
        Blitem.increase_comment_counter(target_id)
        return jsonify({'item': target_id, 'user': user, 'text': text, 'comment_id': c_id})

        #####
        ###     TODO: queue item_id + comment to be added to
        ###     assoc. blibb object
        #####

    return jsonify({'error': 'user not found'})


@mod.route('/<parent_id>', methods=['GET'])
@support_jsonp
@crossdomain(origin='*')
def getComments(parent_id=None):
    if is_valid_id(parent_id):
        cs = Comment.get_comments_by_id(parent_id)
        return jsonify({'comments': cs})
    abort(404)
