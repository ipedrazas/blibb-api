

from flask import Blueprint, request, abort, jsonify, current_app, g, render_template
from API.oiapp.models import Audit
from API.blitem.blitem import Blitem
from API.event.event import Event
from bson.objectid import ObjectId
from API.utils import is_valid_id, read_file, get_config_value
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.decorators import parse_args
import sendgrid



bsm = Blueprint('bsm', __name__, url_prefix='/bsms')

@bsm.route('', methods=['POST'])
@crossdomain(origin='*')
def send_message():
    blitem_id = request.form['id']
    transaction = request.form['transaction']
    app_token = request.form['app_token']

    if is_valid_id(blitem_id):
        blitem = Blitem.get({'_id': ObjectId(blitem_id), 'i.v': transaction})
        flat = Blitem.flat_object(blitem)
        current_app.logger.info(blitem)
        template = read_file('/bsm/templates/mysecretvalentine.html')
        html_mail = template.decode('utf-8')
        html_mail = html_mail.replace("*|IMAGE|*", flat['url'])
        html_mail = html_mail.replace("*|URL|*", 'http://blibb.net/go/' + flat['url_id'])
        html_mail = html_mail.replace("*|MESSAGE|*", flat['message'])

        mail = {
            'to_address': flat['to'],
            'from_name': 'Your Secret Valentine',
            'from': 'mysecretvalentine@blindspotmessenger.com',
            'subject': 'Your Secret Valentine',
            'txt_body': flat['message'],
            'html_body': html_mail
        }

        print 'Mail sent to ' + mail['to_address']
        sendgrid_user = get_config_value('SENDGRID_USER')
        sendgrid_password = get_config_value('SENDGRID_PASSWORD')
        s = sendgrid.Sendgrid(sendgrid_user, sendgrid_password, secure=True)
        message = sendgrid.Message((mail['from'], mail['from_name']), mail['subject'], mail['txt_body'], mail['html_body'])
        message.add_to(mail['to_address'], '')
        s.web.send(message)



