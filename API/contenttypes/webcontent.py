from flask import Blueprint, request, abort, current_app, jsonify
from werkzeug import secure_filename
from werkzeug.wrappers import Response
import json
import os

from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.contenttypes.song import Song
from API.contenttypes.bookmark import Bookmark
from API.contenttypes.picture import Picture
from API.event.event import Event

import API.utils as utils
import API.loader.excel as loader

from API.decorators import crossdomain
from API.decorators import support_jsonp

mod = Blueprint('content', __name__, url_prefix='')

#####################
##### PICTURES  #####
#####################


@mod.route('/image/upload', methods=['POST', 'OPTIONS'])
def upload():
    file = request.files['file']
    if file and utils.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'upload': 'ok'})

    return jsonify({'upload': 'error'})


@mod.route('/picture/data', methods=['POST'])
def set_picture_data():
    e = Event('getImage.set_picture_data')
    pict = Picture()
    jsonData = request.form['p']
    r = pict.updateJson(jsonData)
    e.save()
    if r != 'null':
        return r
    else:
        abort(404)


@mod.route('/picture/<picture_id>', methods=['GET'])
@support_jsonp
def get_picture_data(picture_id=None):
    e = Event('getImage.get_picture_data')
    r = None
    if utils.is_valid_id(picture_id):
        r = Picture.dump_image(picture_id)
    e.save()
    if r is not None:
        return jsonify(r)
    else:
        abort(404)


@mod.route('/picture', methods=['POST'])
def newPicture():
    e = Event('getImage.newPicture')
    pict = Picture()
    blibb = request.form['b']
    key = request.form['k']
    user = utils.get_user_name(key)
    items = dict()
    r = pict.insert(blibb, user, items)
    e.save()
    if r != 'null':
        return r
    else:
        abort(404)


@mod.route('/picture/<pict_id>/<size>', methods=['GET'])
@support_jsonp
def getImage(pict_id=None, size=160):
    e = Event('web.content.getImage')
    r = None
    if utils.is_valid_id(pict_id):
        try:
            img = Picture.dump_image(pict_id)
            g = file(Picture.get_image_by_size(img, size))
            return Response(g, direct_passthrough=True)
        except IOError:
            abort(404)
    e.save()
    if r != 'null':
        return json.dumps(r)
    else:
        abort(404)


@mod.route('/user/pictures/<user_name>', methods=['GET'])
@support_jsonp
def getImageByUsername(user_name=None):
    e = Event('web.content.getImageByUsername')
    p = Picture()
    r = p.getImages({'u': user_name}, {'_id': 1, 'b': 1})
    e.save()
    if r != 'null':
        return json.dumps(r)
    else:
        abort(404)


#####################
#####   SONGS   #####
#####################
@mod.route('/song/data', methods=['POST'])
def setSongData():
    e = Event('web.setSongData')
    song = Song()
    jsonData = request.form['p']
    r = song.updateJson(jsonData)
    e.save()
    if r != 'null':
        return r
    else:
        abort(404)


@mod.route('/song', methods=['POST'])
def newSong():
    e = Event('web.content.newSong')
    song = Song()
    blibb = request.form['b']
    key = request.form['k']
    user = utils.get_user_name(key)
    items = dict()
    r = song.insert(blibb, user, items)
    e.save()
    if r != 'null':
        return r
    else:
        abort(404)

#########################
#####   Bookmarks   #####
#########################


@mod.route('/bkmrk', methods=['POST'])
def newBookmark(song_id=None):
    e = Event('web.content.newBookmark')
    bk = Bookmark()
    t = request.form['title']
    b = request.form['b']
    bn = request.form['bn']
    k = request.form['k']
    user = utils.get_user_name(k)
    url = request.form['url']
    tags = []
    if 'tags' in request.form:
        tags = request.form['tags']
    bk_id = bk.insert(b, user, url, t, bn, tags)
    e.save()
    return  jsonify({'result': str(bk_id)})

####
####
####    Excel Loader
####
####


@mod.route('/loader/excel', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def loader_excel():
    event = Event('web.content.loader_excel')
    key = request.form['login_key']
    bid = request.form['blibb_id']
    user = utils.get_user_name(key)
    res = dict()
    file = request.files['file']
    if file and utils.allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            excel_file = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(excel_file)
            if utils.is_valid_id(bid):
                fields = Blibb.get_fields(bid)
                excel_data = loader.excel_to_dict(excel_file, fields)
                current_app.logger.debug(excel_data)
                if len(excel_data):
                    a = Blitem.bulk_insert(bid, user, excel_data)
                    current_app.logger.debug(a)
                    res['result'] = 'ok'
                else:
                    res['error'] = 'No data found in file'
            else:
                if bid == '-1':
                    res['error'] = 'create new blibb from file'

                res['error'] = 'Object Id is not valid'
        except Exception, e:
            current_app.logger.error(e)
            res['error'] = 'Error processing spreadsheet'

        finally:
            if os.path.isfile(filename):
                os.unlink(filename)

    else:
        res['error'] = 'File was not uploaded'

    event.save()
    return jsonify(res)
