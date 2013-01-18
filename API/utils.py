
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


def parse_text(text):
    return " ".join(text.split())


def is_image(filename):
    allowed_extensions = current_app.config.get('IMAGE_EXTENSIONS')
    return allowed_file(filename, allowed_extensions)


def is_attachment(filename):
    allowed_extensions = current_app.config.get('ATTACHMENT_EXTENSIONS')
    return allowed_file(filename, allowed_extensions)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


def getTitle(url):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        if hasattr(soup, 'head') and hasattr(soup, 'title'):
            return soup.head.title.string.encode('utf-8')

        return ''


def send_url(obj_id, url):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    if obj_id is not None:
        socket.send(str(obj_id + '##' + url))


def get_key(key):
    r = get_redis()
    return r.get(key)


def get_user(key):
    r = get_redis()
    juser = r.get(key)
    # current_app.logger.info("get_user: " + str(juser))
    if juser:
        return json.loads(juser)
    return None


def get_user_name(key):
    r = get_redis()
    juser = r.get(key)
    expire = current_app.config.get('EXPIRE')
    r.expire(key, expire)
    if juser:
        user = json.loads(juser)
        return user['username']


def get_email(key):
    r = get_redis()
    juser = r.get(key)
    if juser:
        user = json.loads(juser)
        return user['email']


def get_redis():
    return redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


def queue_twitter_resolution(obj_id, twiter_screen_name):
    print 'Queuing to twitter worker ' + str(obj_id)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    if obj_id is not None:
        socket.send(str(obj_id + '##' + twiter_screen_name))


def queue_ducksboard_delta(widget_id, value=1, timestamp=False):
    if widget_id is not None:

        if timestamp:
            msg = widget_id + '##'+ str(value) +'##td'
        else:
            msg = widget_id + '##'+ str(value) +'##d'
        queue_ducksboard(widget_id, msg)


def queue_ducksboard_value(widget_id, value):
    if widget_id is not None:
        msg = '%s##%s##v' % (widget_id, value)
        queue_ducksboard(widget_id, msg)


def queue_mail(oiid, full_name, name, email, comments):
    print 'Queuing to mail worker ' + str(oiid)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558")
    if oiid is not None:
        # oiid, full_name, name, email, comments
        msg = '%s##%s##%s##%s##%s' % (oiid, full_name, name, email, comments)
        socket.send(msg)


def queue_ducksboard(widget_id, msg):
    print 'Queuing to ducksboard worker ' + str(widget_id)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")
    if widget_id is not None:
        socket.send(msg)


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


def get_config_value(key=None):
    json_data = open('/var/blibb/settings.json')
    data = json.load(json_data)
    json_data.close()
    return data.get(key, '')

