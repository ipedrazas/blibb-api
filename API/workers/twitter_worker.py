#twitter_test.py

import json
from httplib2 import Http
import zmq
import time
import logging

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)


from API.control.bcontrol import BControl
from API.blitem.blitem import Blitem
from urllib import urlencode


def readQueue(message):
	strs = message.split('##')
	o_id = strs[0]
	screen_name = strs[1]
	return {'id':o_id, 'name' : screen_name}


def getTwitterDetails(user_names, attributes):
	users = []
	if user_names:
		h = Http()
		screen_names = ','.join(user_names)
		post_params = dict(screen_name= screen_names, include_entities= False)
		twitter_url = "https://api.twitter.com/1/users/lookup.json"
		resp,json_content = h.request(twitter_url, 'POST', urlencode(post_params))
		limit = resp.get('x-ratelimit-remaining')
		content = json.loads(json_content)
		for user in content:
			if type(user)==type({}):
				u = dict()
				for att in attributes:
					u[att] = user.get(att)
				users.append(u)
			else:
				users.append(user)
	return users

def getScreenNames(names):
	screen_names = []
	for name in names:
		screen_names.append(name.get('name'))
	return screen_names

def processTwitterData(users, attributes):
	lean_users = []
	for user in users:
		u = dict()
		if type(user)==type({}):
			for att in attributes:
				u[att] = user.get(att)			
		else:
			u['screen_name'] = user
			u['name'] = 'not found'
			u['location'] = 'not found'
			u['description'] = 'not found'
			u['profile_image_url'] = ''
		lean_users.append(u)

	return lean_users


def updateTwitterItem(user_list, namesBag):
	for user in user_list:
		name = user.get('screen_name')
		logger.debug('Updating ' + str(user) + ' with ' + name)
		u_id = getObjectId(name, namesBag)
		if u_id is not None:
			print 'Update Item ' + str(u_id) + ' with ' + str(user)
			blitem = Blitem()
			blitem.load(u_id)
			blitem.populate()
			items = blitem.items
			for item in items:
				if BControl.isTwitter(item['t']):
					item['v'] = user
			
			blitem.items = items
			blitem.save()

def getObjectId(name,namesBag):
	for e in namesBag:
		if name == e.get('name'):
			return e.get('id')


logger = logging.getLogger('twitter_worker')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
atts = ['screen_name','name','description', 'profile_image_url', 'location']
start_time = time.time()	
namesBag = []
while True:
	#  Wait for next request from client
	time.sleep (0.1) 
	lap = time.time() - start_time
	if lap > 25:
		if(len(namesBag)>0):
			names_list =  getScreenNames(namesBag)
			twitter_details = getTwitterDetails(names_list, atts)
			user_list = processTwitterData(twitter_details, atts)
			updateTwitterItem(user_list, namesBag)
			del namesBag[:]
		start_time = time.time()

	try: 
		message = socket.recv(zmq.NOBLOCK)
		namesBag.append(readQueue(message))
		socket.send('ok')
	except zmq.ZMQError as e:
		if e.errno != zmq.EAGAIN:
			raise
