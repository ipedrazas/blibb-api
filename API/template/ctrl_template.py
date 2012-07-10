# 
#
#   template.py
#
#

from flask import current_app

from datetime import datetime
from bson.objectid import ObjectId
from pymongo import Connection
from API.helpers import slugify
import API.utils as utils
import json

conn = Connection()
db = conn['blibb']
objects = db['templates']


class ControlTemplate(object):

    @classmethod
    def addControl(self, cid, tid, name, help, order, view, slug, typex):
        view = {'c': cid,  'n': name, 'h': help, 's': slug, 'o': order, 'w': view, 'tx': typex}
        objects.update({'_id': ObjectId(tid)}, {"$push": {'i': view}}, True)
        return cid

    @classmethod
    def insert(self, name, desc, user, thumbnail, status="draft"):
        now = datetime.utcnow()
        doc = {"n": name, "d": desc, "u": user, "c": now, "s": slugify(name), 't': thumbnail, 'q': status}
        newId = objects.insert(doc)
        return str(newId)

    @classmethod
    def add_controls(self, template_id, controls, user):
        items = []
        if utils.is_valid_id(template_id):
            controls = json.loads(controls)
            for control in controls:
                item = {}
                cid = control.get('cid', '')
                if utils.is_valid_id(cid):
                    item['c'] = ObjectId(cid)
                item['n'] = control['name']
                item['h'] = control['help']
                item['tx'] = int(control['type'])
                item['o'] = int(control['order'])
                item['s'] = slugify(control['name'])

                # control_name = control['type'] + '-' + control['name']
                # control_id = cid + '-' + control['order']
                # #html = '<div id="'+ control_id +'" class="control class"><label for="'+control_name+'">'+control['name']+':</label><input name="'+control_name+'" placeholder="'+control['help']+'" size="50" type="text" /></div>'
                # #item['w'] = html
                items.append(item)
            current_app.logger.info(items)
            objects.update({'_id': ObjectId(template_id)}, {'$set': {'i': items}})

    @classmethod
    def get_object(self, filter, fields={}):
        if len(fields) > 0:
            doc = objects.find_one(filter, fields)
        else:
            doc = objects.find_one(filter)
        return doc

    @classmethod
    def get_templates(self, filter, fields, page=1):
        PER_PAGE = 20
        docs = objects.find(filter, fields).sort("c", -1).skip(PER_PAGE * (page - 1)).limit(PER_PAGE)
        return docs

    @classmethod
    def flat_object(self, doc):
        buf = dict()
        if doc:
            buf['id'] = str(doc['_id'])
            if 'n' in doc:
                buf['name'] = doc['n']
            if 'c' in doc:
                buf['date'] = str(doc['c'])
            if 'u' in doc:
                buf['owner'] = doc['u']
            if 's' in doc:
                buf['slug'] = doc['s']
            if 'q' in doc:
                buf['status'] = doc['q']
            if 't' in doc:
                buf['thumbnail'] = doc['t']
            if 'i' in doc:
                buf['controls'] = doc['i']

        return buf

    @classmethod
    def flaf_control(self, control):
        c = {}
        current_app.logger.info('flat_control: ' + str(control))
        if control:
            c['control_id'] = str(control['c'])
            c['type'] = control['tx']
            c['name'] = control['n']
            c['slug'] = control['s']
            c['order'] = control['o']
        return c

    @classmethod
    def get_by_id(self, template_id):
        if utils.is_valid_id(template_id):
            doc = self.get_object({'_id': ObjectId(template_id)})
            return self.flat_object(doc)
        else:
            return None

    @classmethod
    def get_templates_by_user(self, username, page=0):
        templates = []
        docs = self.get_templates({'u': username}, {'i': 0})
        for doc in docs:
            templates.append(self.flat_object(doc))

        return templates

    @classmethod
    def publish(self, view_name, template_id):
        html_read = ''
        html_write = ''
        if utils.is_valid_id(template_id):
            template = self.get_by_id(template_id)
            # get controls
            controls = template.get('controls')
            if controls:
                for control in controls:
                    c = self.flaf_control(control)
                    html_read += self.get_read_html(c)
                    html_write += self.get_write_html(c)

                # w rb sb ri si
                res = dict()
                res['rb'] = html_read
                res['wb'] = html_write

                objects.update({'_id': ObjectId(template_id)}, {"$push": {'v.' + view_name: res}, '$set': {'q': 'active'}}, True)
                return True
        return False

    @classmethod
    def get_read_html(self, control):
        current_app.logger.info(control)
        return '<div class="%(slug)s">{{{%(slug)s}}}</div>' % control

    @classmethod
    def get_write_html(self, control):
        html = ('<div id="%(control_id)s_%(slug)s" class="templatedCtrl">'
                    '<label for="%(type)s-%(slug)s">%(name)s:</label>'
                    '<input name="%(type)s-%(slug)s" placeholder="" size="50" type="text" /> '
                '</div>') % control
        return html
