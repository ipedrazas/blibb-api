
from API.om.manager import Manager
from flask import Blueprint, request, abort, jsonify
from API.decorators import crossdomain
from API.decorators import support_jsonp


mod = Blueprint('manager', __name__, url_prefix='/sys')


@mod.route('/validate/<code>', methods=['GET'])
@support_jsonp
def validate(code=None):
    return jsonify({'result': Manager.validateCode(code)})


@mod.route('/add/tobeta', methods=['POST'])
@crossdomain(origin='*')
def add_to_beta_list():
    email = request.form['email']
    ip = request.form['ip']
    browser = request.form['browser']

    res = {'result': Manager.addBetaUser(email, ip, browser)}
    return jsonify(res)


@mod.route('/add/code', methods=['POST'])
@crossdomain(origin='*')
def add_code():
    key = request.form['k']
    code = request.form['c']
    if key == 'ivan':
        res = {'result': Manager.addCode(code)}
        return jsonify(res)
    else:
        abort(401)


@mod.route('/url/<url_id>', methods=['GET'])
def get(url_id=None):
    if url_id:
        blibb = Blibb.get_object({'url_id': url_id})
        if blibb:
            return redirect('http://blibb.net/blibb?b=' + str(blibb['_id']), 301)
    abort(404)


def short_id(link):
        url_id = "".join(sample(digits + ascii_letters, num))
        objects.insert({'url_id': url_id, 'link': link, 'hits': 0, 'saved': 0, 'added': datetime.utcnow()})
        return url_id


@mod.route('url/', methods=['POST'])
def add():
    link = request.form['link']
    auth_token = request.form['key']
    if auth_token != SECRET:
        abort(401)
    url = objects.find_one({'link': link})
    if url:
        objects.update({'_id': url['_id']}, {'$inc': {'saved': 1}})
        return jsonify({'url': URL + url['url_id']})
    else:
        return jsonify({'url': URL + short_id(link)})


def date_to_str(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%d-%m-%Y- %H:%M:%S')
