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
from API.control.bcontrol import Control
import API.utils as utils
import json
import pystache

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
        current_app.logger.info("add_controls " + str(controls))
        if utils.is_valid_id(template_id):
            controls = json.loads(controls)
            for control in controls:
                item = {}
                cid = control.get('cid', '')
                if utils.is_valid_id(cid):
                    item['c'] = ObjectId(cid)
                    item['n'] = control['name']
                    item['h'] = control['help']
                    item['tx'] = control['type']
                    item['o'] = int(control['order'])
                    item['s'] = slugify(control['name'])
                    if 'items' in control:
                        item['i'] = control.get('items')
                    items.append(item)
                else:
                    current_app.logger.info('Control ID' + cid)
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
            if 'v' in doc:
                buf['views'] = doc['v']

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
            if 'i' in control:
                c['items'] = control['i']
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
                    html = self.get_html(c)
                    html_read += html.get('read', '')
                    html_write += html.get('write', '')

                res = dict()
                data = dict()
                data['entry'] = html_read
                res['ri'] = html_read
                res['rb'] = self.get_blibb_template_wrapper(data)
                res['wb'] = html_write

                objects.update({'_id': ObjectId(template_id)}, {"$push": {'v.' + view_name: res}, '$set': {'q': 'active'}}, True)
                return True
        return False

    @classmethod
    def get_blibb_template_wrapper(self, data):
        html = utils.read_file('/scripts/templates/base/base.html')
        return html.replace('<blibb:entry/>', data['entry'])

    @classmethod
    def get_html(self, control):
        view = Control.get_view_by_id(control['control_id'])
        current_app.logger.info('view html: ' + str(view) + ' ' + str(control))
        read = pystache.render('{{=<% %>=}}' + view['read'], control)
        write = pystache.render('{{=<% %>=}}' + view['write'], control)
        current_app.logger.info('write html: ' + write)
        return {'read': read, 'write': write}
