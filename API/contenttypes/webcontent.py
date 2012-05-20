
import redis
from flask import Blueprint, request, redirect, abort
import json

from API.contenttypes.song import Song
from API.contenttypes.picture import Picture
from API.event.event import Event


mod = Blueprint('content', __name__, url_prefix='')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is content'"



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
	user = getKey(key)
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
	user = getKey(key)
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
	user = getKey(k)
	url = request.form['url']
	tags = []
	if 'tags' in request.form:
		tags = request.form['tags']
	bk_id = bk.insert(b, user, url, t, bn, tags )
	return  json.dumps(bk_id,default=json_util.default)



def getKey(key):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	return r.get(key)