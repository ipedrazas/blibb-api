
import redis
from flask import Blueprint, request, redirect, abort, current_app, jsonify
from werkzeug import secure_filename
import json
import os

from API.blitem.blitem import Blitem
from API.blibb.blibb import Blibb
from API.contenttypes.song import Song
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

@mod.route('/image/upload', methods=['POST','OPTIONS'])
def upload():
	file = request.files['file']
	if file and utils.allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
		return jsonify({'upload': 'ok'})

	return jsonify({'upload': 'error'})
	 
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

####
####
####	Excel Loader
####
####
@mod.route('/loader/excel', methods=['POST','OPTIONS'])
@crossdomain(origin='*')
def loader_excel():
	event = Event('web.content.loader_excel')
	key = request.form['login_key']
	bid = request.form['blibb_id']
	user = utils.getKey(key)
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



