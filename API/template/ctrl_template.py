#
#
#   template.py
#
#

# from flask import current_app

from datetime import datetime
from bson.objectid import ObjectId
from pymongo import Connection
from API.helpers import slugify
from API.control.bcontrol import Control
from API.utils import is_valid_id, read_file, parse_text
from API.utils import get_config_value
import json
import pystache

# from flask import current_app


conn = Connection(get_config_value('MONGO_URL'))
db = conn['blibb']
objects = db['templates']


class ControlTemplate(object):

    @classmethod
    def insert(self, name, desc, user, thumbnail, status="draft"):
        now = datetime.utcnow()
        doc = {
            "n": name,
            "d": desc,
            "u": user,
            "c": now,
            "s": slugify(name),
            't': thumbnail,
            'q': status}
        newId = objects.insert(doc)
        return str(newId)

    @classmethod
    def add_controls(self, template, controls, user):
        items = []
        # current_app.logger.info("add_controls " + str(controls))
        controls = json.loads(controls)
        for control in controls:
            item = {}
            cid = control.get('cid', '')
            if is_valid_id(cid):
                item['c'] = ObjectId(cid)
                item['n'] = control['name']
                item['h'] = control['help']
                item['tx'] = control['type']
                item['o'] = int(control['order'])
                item['s'] = slugify(control['name'])
                item['m'] = True if control['multi'] == 'true' else False
                if 'items' in control:
                    item['i'] = control.get('items')
                items.append(item)
            # else:
                # current_app.logger.info('Control ID' + cid)
        # current_app.logger.info(items)
        now = datetime.utcnow()
        doc = {
            "n": template,
            "u": user,
            "c": now,
            "s": slugify(template),
            'q': 'draft', 'i': items}
        newId = objects.insert(doc)
        return str(newId)

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
        docs = objects.find(filter, fields).sort("c", -1).skip(
            PER_PAGE * (page - 1)).limit(PER_PAGE)
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
        # current_app.logger.info('flat_control: ' + str(control))
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
        if is_valid_id(template_id):
            doc = self.get_object({'_id': ObjectId(template_id)})
            return self.flat_object(doc)
        else:
            return None

    @classmethod
    def get_templates_flat(self, filter, fields):
        docs = objects.find(filter, fields)
        templates = []
        for doc in docs:
            templates.append(self.flat_object(doc))
        return templates

    @classmethod
    def publish_default(cls, template_id):
        html_read = ''
        html_write = ''
        table_head = ''
        row = '<tr>'
        html_table = read_file('/scripts/templates/base/table.html')
        if is_valid_id(template_id):
            template = cls.get_by_id(template_id)
            # get controls
            controls = template.get('controls')
            if controls:
                for control in controls:
                    c = cls.flaf_control(control)
                    html = cls.get_html(c)
                    html_read += html.get('read', '')
                    html_write += html.get('write', '')
                    table_head += '<th>' + c['name'] + '</th>'
                    row += '<td>{{{' + c['slug'] + '}}}</td>'

                html_table = html_table.replace(
                    '<blibb:entry value="labels"/>', table_head)
                html_table = html_table.replace('<blibb:entry/>', row)
                res = dict()
                data = dict()
                data['entry'] = html_read
                res['ri'] = parse_text(html_read)
                res['rb'] = parse_text(cls.get_blibb_template_wrapper(data))
                res['wb'] = parse_text(html_write)
                box = {'name': 'default', 'view': res}
                cls.publish(box, template_id)
                table_dict = dict()
                table_dict['ri'] = parse_text('<td>{{' + c['slug'] + '}}</td>')
                table_dict['rb'] = parse_text(html_table)
                table = {'name': 'table', 'view': table_dict}
                return cls.publish(table, template_id)
        return False

    @classmethod
    def publish(cls, object, template_id):
        '''view is a dict that contains:
            name: name of the view
            view: dict that contains
                ri: read item, html to render the item when accessing as RO
                rb: read blibb, html to render the whole blibb when a
                    ccessing as RO
                wb: write blibbb, html to create/edit new items
        '''
        # current_app.logger.info(str(object))
        objects.update({'_id': ObjectId(template_id)}, {
            "$set": {
                'v.' + object.get('name'): object.get('view'),
                'q': 'active'}}, True)
        return True

    @classmethod
    def get_blibb_template_wrapper(self, data):
        html = read_file('/scripts/templates/base/base.html')
        return html.replace('<blibb:entry/>', data['entry'])

    @classmethod
    def get_html(self, control):
        view = Control.get_view_by_id(control['control_id'])
        read = pystache.render('{{=<% %>=}}' + view['read'], control)
        write = pystache.render('{{=<% %>=}}' + view['write'], control)
        # current_app.logger.info('write html: ' + write)
        return {'read': read, 'write': write}
