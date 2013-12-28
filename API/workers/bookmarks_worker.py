# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display

from __future__ import division
import zmq
import sys
from os.path import join, abspath, dirname
import time


parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.utils import get_config_value


print "URL Worker running at port 5559"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5559")

def get_bookmark(url, oid, owner):

	display = Display(visible=0, size=(800, 600))
	display.start()
	result = {}
	# url = 'http://kcy.me/wge8'
	result['original-url'] = url
	req = requests.get(url)
	result['url'] = req.url


	soup = BeautifulSoup(req.text, 'lxml')
	result['title'] = soup.title.string.encode('utf-8')
	result['description'] = soup.findAll(attrs={"name":"description"})[0]['content'].encode('utf-8')


	driver = webdriver.Firefox()
	driver.get(req.url)
	filename = oid + '.png'
	fname = os.path.join(os.path.dirname(__file__), filename)

	result['screenshot'] = upload_image_as_png_to_s3(filename, owner)

	driver.get_screenshot_as_file(fname)
	driver.close()

	display.stop()

	# delete temp file
	os.unlink(filename)

	return result


def update_bookmark(oid, bookmark):
    if oid and bookmark:
        blitem = Blitem.get({'_id': ObjectId(oid)})
        items = blitem['i']
        for item in items:
            type = item['t']
            if ControlType.is_bookmark(type):
                item['v'] = bookmark
        logger.debug(str(blitem))
        Blitem.save(blitem)


def processMessage(message):
	url = message.get('url', None)
	oid = message.get('oid', None)
	owner = message.get('owner', None)
	if url and oid and owner:
		bookmark = get_bookmark()
		update_bookmark(oid, bookmark)

while True:
    msg = socket.recv_json()
    print str(msg)
    processMessage(msg)

    #  Do some 'work'
    time.sleep(1)  # Do some 'work'
    socket.send('ok')

socket.close()
context.term()
