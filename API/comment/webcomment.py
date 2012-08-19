

from flask import Blueprint, request, current_app, jsonify
from API.comment.comment import Comment
from API.event.event import Event
from API.blitem.blitem import Blitem
import API.utils as utils

from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('comment', __name__, url_prefix='/comment')


@mod.route('/hi')
def hello_world():
    return "Hello World, this is comment'"


#####################
##### COMMENTS  #####
#####################

@mod.route('', methods=['POST'])
@crossdomain(origin='*')
def newComment():
    e = Event('web.newComment')
    comment = Comment()
    key = request.form['login_key']
    target_id = request.form['item_id']
    text = request.form['comment']
    user = utils.get_user_name(key)
    if user is not None:
        pObject = Blitem()
        c_id = comment.insert(target_id, user, text)
        pObject.increase_comment_counter(target_id)
        return jsonify({'item': target_id, 'user': user, 'text': text, 'comment_id': c_id})

        #####
        ###     TODO: queue item_id + comment to be added to
        ###     assoc. blibb object
        #####

    e.save()
    return jsonify({'error': 'user not found'})


@mod.route('/<parent_id>', methods=['GET'])
@support_jsonp
def getComments(parent_id=None):
    e = Event('web.getComments')
    comment = Comment()
    cs = comment.getCommentsById(parent_id)
    e.save()

    return jsonify({'comments': cs})
