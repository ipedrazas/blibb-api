
from bs4 import BeautifulSoup
import urllib2
from os.path import join, abspath, dirname
from bson.objectid import ObjectId
import zmq
import redis
from flask import current_app
from unicodedata import normalize
import re
from bson import errors
import json
import datetime


def allowed_file(filename):
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS')
    # allowed_extensions = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in allowed_extensions


def getTitle(url):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        if hasattr(soup, 'head') and hasattr(soup, 'title'):
            return soup.head.title.string.encode('utf-8')

        return ''


def sendUrl(obj_id, url):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    if obj_id is not None:
        socket.send(str(obj_id + '##' + url))


def get_key(key):
    r = get_redis()
    return r.get(key)


def get_user_name(key):
    r = get_redis()
    juser = r.get(key)
    if juser:
        user = json.loads(juser)
        return user['username']


def get_redis():
    return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


def queueTwitterResolution(obj_id, twiter_screen_name):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    if obj_id is not None:
        socket.send(str(obj_id + '##' + twiter_screen_name))


def is_valid_id(obj_id):
        try:
            ObjectId(obj_id)
            return True
        except errors.InvalidId:
            return False
        except TypeError:
            return False


def read_file(filename):
    path = abspath(join(dirname(__file__), '.')) + filename
    print path
    f = open(path, 'r')
    return f.read()


def slugify(text, delim=u''):
    """Generates an slightly worse ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?:@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', unicode(word)).encode('ascii', 'ignore')
        if word is not None:
            result.append(word)

    return unicode(delim.join(result))


def date_to_str(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%d-%m-%Y- %H:%M:%S')
