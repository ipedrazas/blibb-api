

from flask import Blueprint, request, abort, current_app, jsonify
from werkzeug import secure_filename
from werkzeug.wrappers import Response
import json
import os

from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.contenttypes.bookmark import Bookmark
from API.contenttypes.picture import Picture
from API.event.event import Event
from API.utils import get_user_name, allowed_file,  is_valid_id
from API.utils import is_image, is_attachment, get_config_value
import API.loader.excel as loader

from API.decorators import crossdomain
from API.decorators import support_jsonp

from boto import connect_s3
from boto.s3.key import Key


mod = Blueprint('content', __name__, url_prefix='')

#####################
##### PICTURES  #####
#####################


@mod.route('/image/upload', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def upload():
    current_app.logger.info('Upload Image')
    login_key = request.form.get('login_key', False)
    # app_token = request.form.get('app_token', False)
    app_user = request.form.get('u', False)

    if login_key:
        user = get_user_name(login_key)
    else:
        user = app_user

    if 'file' in request.files:
        file = request.files['file']
        object_id = Picture.create(user, {}, file.filename)
        filename = secure_filename(object_id + '-' + file.filename)
        c = connect_s3()
        bucket_name = get_config_value('BUCKET')
        bucket = c.create_bucket(bucket_name)
        k = Key(bucket)
        k.key = user + '/' + filename
        k.set_metadata('owner', user)
        extension = os.path.splitext(filename)[1]
        k.content_type = file.content_type
        current_app.logger.info('Extension: ' + str(extension))
        current_app.logger.info('file.content_type: ' + str(file.content_type))
        if extension.lower() == '.jpg':
            k.content_type = 'image/jpeg'
        if extension.lower() == '.png':
            k.content_type = 'image/png'
        if extension.lower() == '.gif':
            k.content_type = 'image/gif'
        current_app.logger.info('Extension: ' + str(extension))
        current_app.logger.info('file.content_type: ' + str(k.content_type))
        k.set_contents_from_string(file.read())
        k.make_public()
        url = 'http://%s/%s' % (bucket_name, k.key)
        current_app.logger.info(
            '########## url: ' + str(url) + ' ' + str(bucket)
        )
        if is_image(file.filename):
            Picture.add_url(object_id, url)
        elif is_attachment(file.filename):
            object_id = Picture.add_url(file.filename)

        return jsonify({'upload': url})
    return jsonify({'upload': 'error'})


@mod.route('/picture/data', methods=['POST'])
@crossdomain(origin='*')
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
@crossdomain(origin='*')
@support_jsonp
def get_picture_data(picture_id=None):
    e = Event('getImage.get_picture_data')
    r = None
    if is_valid_id(picture_id):
        r = Picture.dump_image(picture_id)
    e.save()
    if r is not None:
        return jsonify(r)
    else:
        abort(404)


@mod.route('/picture', methods=['POST'])
@crossdomain(origin='*')
def newPicture():
    e = Event('getImage.newPicture')
    pict = Picture()
    blibb = request.form['b']
    key = request.form['k']
    user = get_user_name(key)
    items = dict()
    r = pict.insert(blibb, user, items)
    e.save()
    if r != 'null':
        return r
    else:
        abort(404)


@mod.route('/picture/<pict_id>/<size>', methods=['GET'])
@crossdomain(origin='*')
@support_jsonp
def getImage(pict_id=None, size=160):
    e = Event('web.content.getImage')
    r = None
    if is_valid_id(pict_id):
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
@crossdomain(origin='*')
@support_jsonp
def getImageByUsername(user_name=None):
    r = Picture.get_images({'u': user_name}, {'_id': 1, 'b': 1})
    current_app.logger.info(r)
    if r and len(r) > 0:
        return jsonify({'images': r})
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
    user = get_user_name(k)
    url = request.form['url']
    tags = []
    if 'tags' in request.form:
        tags = request.form['tags']
    bk_id = bk.insert(b, user, url, t, bn, tags)
    e.save()
    return jsonify({'result': str(bk_id)})

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
    user = get_user_name(key)
    res = dict()
    file = request.files['file']
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            excel_file = os.path.join(
                get_config_value('UPLOAD_FOLDER'), filename
            )
            file.save(excel_file)
            if is_valid_id(bid):
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
        # except Exception, e:
            # current_app.logger.error(e)
            # res['error'] = 'Error processing spreadsheet'

        finally:
            if os.path.isfile(filename):
                os.unlink(filename)

    else:
        res['error'] = 'File was not uploaded'

    event.save()
    return jsonify(res)
