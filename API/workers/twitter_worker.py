#twitter_test.py

import json
import httplib2
import zmq
import time

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)


from API.control.bcontrol import BControl
from API.blitem.blitem import Blitem



def readQueue(message):
	strs = message.split('##')
	o_id = strs[0]
	screen_name = strs[1]
	return {'id':o_id, 'name' : screen_name}


def getTwitterDetails(user_names, attributes):	
	users = []
	if user_names:
		h = httplib2.Http(".cache")
		strUser = ','.join(user_names)	
		twitter_url = "https://api.twitter.com/1/users/lookup.json?screen_name={0}&include_entities=false".format(strUser)
		print twitter_url
		resp,json_content = h.request(twitter_url)
		
		limit = resp.get('x-ratelimit-remaining')

		content = json.loads(json_content)
		for user in content:
			u = dict()
			print user
			for att in attributes:
				u[att] = user.get(att)
			# u = {'screen_name': user.get('screen_name'),'name': user.get('name'), 'description': user.get('description'), 'image': user.get('profile_image_url'), 'location': user.get('location')}
			users.append(u)
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
		for att in attributes:
			u[att] = user.get(att)
		lean_users.append(u)
	return lean_users


def updateTwiterItem(user_list, namesBag):
	for user in user_list:
		name = user.get('screen_name')
		u_id = getObjectId(name, namesBag)
		print 'Update Item ' + u_id + ' with ' + str(user)
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
			updateTwiterItem(user_list, namesBag)
			del namesBag[:]
		start_time = time.time()

	try: 
		message = socket.recv(zmq.NOBLOCK)
		namesBag.append(readQueue(message))
		socket.send('ok')
	except zmq.ZMQError as e:
		if e.errno != zmq.EAGAIN:
			raise
