#
#


from flask import Blueprint, request, abort, jsonify, current_app, g
from API.oiapp.models import Oi
from API.event.event import Event


from API.utils import get_user_name
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
    owner = get_user_name(login_key)
    if owner:
        contacts = request.form['contacts']
        name = request.form['name']
        current_app.logger.info(owner)
        doc = Oi.create(owner, name, contacts)
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
