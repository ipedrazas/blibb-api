###
###
###		project: bapi
###		createTemplate.py
###
###

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.template.template import Template


def readFile(filename):
	path = abspath(join(dirname(__file__), '.')) + filename
	print path
	f = open(path, 'r')
	return f.read()


def createBlogTemplate():
	template = Template()
	name = ':blibb blog'
	desc = 'Where amazing content happens'
	author = 'ipedrazas'
	status = 'active'
	
	new_id =template.insert(name, desc, author, 'blog.thumbnail.png', status)

	template.addControl('4f835931db035984e312193b',new_id,'Title','Post Title', '1', '<label for="01-title">Title:</label><input name="01-title" placeholder="Post Title" size="50" type="text" />','title', '01')
	template.addControl('4f835931db035984e312193b',new_id,'Body','Post Body', '2', '<label for="b-fbsdfbd">Body:</label><textarea rows="5" cols="50" name="02-body" placeholder="Post Body"></textarea>', 'body',  '02')
	template.addControl('4f835931db035984e312193b',new_id,'Month','Month', '3', '<label for="01-month">Month:</label><input name="01-month" placeholder="month" size="50" type="text" />', 'month', '01')
	template.addControl('4f835931db035984e312193b',new_id,'Day','Day', '4', '<label for="01-day">Day:</label><input name="01-day" placeholder="day" size="50" type="text" />','day', '01')

	rb = readFile('/templates/blog/blog.html')
	sb = readFile('/templates/blog/blog.css')
	ri = ''#readFile('/templates/blog/blog-entry.html')
	si = ''#readFile('/templates/blog/blog-entry.css')
	template.addView(new_id, 'Default', rb, sb, ri, si)

def createBookmarkTemplate():
	template = Template()
	name = ':blibb bookmarks'
	desc = 'A simpler way of managing bookmarks'
	author = 'ipedrazas'
	status = 'active'
	
	new_id =template.insert(name, desc, author, 'blog.thumbnail.png', status)

	template.addControl('4f835931db035984e312193b',new_id,'Url','Bookmark Url', '2', '<label for="01-url">Url:</label><input name="33-url" placeholder="Url" size="50" type="text" />', 'url', '33')
	
	rb = readFile('/templates/bookmark/bookmarks.html')
	sb = readFile('/templates/bookmark/bookmarks.css')
	ri = ''#readFile('/templates/bookmark/bookmark-entry.html')
	si = ''#readFile('/templates/bookmark/bookmark-entry.css')
	template.addView(new_id, 'Default', rb, sb, ri, si)


def addControl(self, cid, tid, name, help, order, view, slug, ctype, typex):
		view = {'c': cid,  'n': name, 'h': help, 's': slug, 'o': order, 'w': view, 't': ctype, 'tx': typex}
		self.objects.update({ u'_id': ObjectId(tid)}, {"$push": {'i': view}}, True)
		return cid

createBlogTemplate()
createBookmarkTemplate()
