#twitter_test.py

import json
import httplib2


def getTwitterDetails(user_names, attributes):	
	h = httplib2.Http(".cache")
	strUser = ','.join(user_names)	
	twitter_url = "https://api.twitter.com/1/users/lookup.json?screen_name={0}&include_entities=false".format(strUser)
	# print twitter_url
	resp,json_content = h.request(twitter_url)
	# print json_content
	print resp.get('x-ratelimit-remaining')
	content = json.loads(json_content)
	users = []
	for user in content:
		u = dict()
		for att in attributes:
			u[att] = user.get(att)
		# u = {'screen_name': user.get('screen_name'),'name': user.get('name'), 'description': user.get('description'), 'image': user.get('profile_image_url'), 'location': user.get('location')}
		users.append(u)
	return users


atts = ['screen_name','name','description', 'profile_image_url', 'location']
user_names = ['valgreens','ipedrazas']
users = getTwitterDetails(user_names, atts)
for u in users:
	print u

