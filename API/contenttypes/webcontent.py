
import redis
from flask import Blueprint, request, redirect, abort,current_app
from werkzeug import secure_filename
import json
import os

from API.contenttypes.song import Song
from API.contenttypes.picture import Picture
from API.event.event import Event
import API.utils as utils

mod = Blueprint('content', __name__, url_prefix='')


@mod.route('/image/upload', methods=['POST','OPTIONS'])
def upload():
	file = request.files['file']
	if file and utils.allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
		return jsonify({'return': 'ok'})
	return jsonify({'error': 'unable to upload file'})




#####################
##### PICTURES  #####
#####################
@mod.route('/picture/data', methods=['POST'])
def setPictureData():
	e = Event('getImage.setPictureData')
	pict = Picture()
	jsonData = request.form['p']
	r = pict.updateJson(jsonData)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

@mod.route('/picture', methods=['POST'])
def newPicture():
	e = Event('getImage.newPicture')
	pict = Picture()
	blibb = request.form['b']
	key = request.form['k']
	user = utils.getKey(key)
	items = dict()
	r = pict.insert(blibb,user,items)
	e.save()
	if r != 'null':
		return r
	else:
		abort(404)

@mod.route('/picture/<pict_id>', methods=['GET'])
def getImage(pict_id=None):
	e = Event('web.content.getImage')
	p = Picture()
	r = p.dumpImage(pict_id)
	e.save()
	if r != 'null':
		return json.dumps(r)
	else:
		abort(404)

@mod.route('/user/pictures/<user_name>', methods=['GET'])
def getImageByUsername(user_name=None):
	e = Event('web.content.getImageByUsername')
	p = Picture()
	r = p.getImages({'u': user_name},{'_id','b'})
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
	user = utils.getKey(key)
	items = dict()
	r = song.insert(blibb,user,items)
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
	user = utils.getKey(k)
	url = request.form['url']
	tags = []
	if 'tags' in request.form:
		tags = request.form['tags']
	bk_id = bk.insert(b, user, url, t, bn, tags )
	return  json.dumps(bk_id,default=json_util.default)

