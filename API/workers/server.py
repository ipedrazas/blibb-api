#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects "Hello" from client, replies with "World"
#
import zmq
import time

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.blitem.blitem import Blitem
from API.contenttypes.bookmark import Bookmark
import API.utils as utils
from API.control.bcontrol import BControl

import logging

print "URL Worker running"

logger = logging.getLogger('URL Worker')
hdlr = logging.FileHandler(dirname(__file__) + 'urlWorker.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def processUrl(message):
	strs = message.split('##')
	url = strs[1]
	title = utils.getTitle(url)
	blitem = Blitem()
	blitem.load(strs[0])
	blitem.populate()
	logger.debug(blitem.id)
	bkmrk = Bookmark()
	bk_id = bkmrk.findByUrl(url)
	logger.debug("Bookmark: " + str(bk_id))
	if bk_id is None:
		logger.debug("Bookmark Insert")
		bk_id = bkmrk.insert(blitem.blibb, blitem.owner, url, title, blitem.tags)
		bkmrk.load(bk_id)
	else:
		logger.debug("Bookmark Update")
		bkmrk.add(blitem.blibb,blitem.owner,blitem.tags)

	items = blitem.items
	for item in items:
		if BControl.isURL(item['t']):
			bk = bkmrk.dumpBookmark()
			item['v'] = bk
	
	blitem.items = items
	blitem.save()
	return bk_id


while True:
    #  Wait for next request from client
    message = socket.recv()
    print "Received request: ", message
    print processUrl(message)
    #  Do some 'work'
    time.sleep (1)        #   Do some 'work'
    socket.send('ok')




