#
#
#   worker Mail
#
#
from __future__ import division
import zmq
import sys
from os.path import join, abspath, dirname
import sendgrid

parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.utils import get_config_value


print "URL Worker running at port 5558"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")


def send_invitation_mail(mail):
    current_app.logger.info('Mail sent to ' + mail['to_address'])
    sendgrid_user = get_config_value('SENDGRID_USER')
    sendgrid_password = get_config_value('SENDGRID_PASSWORD')
    s = sendgrid.Sendgrid(sendgrid_user, sendgrid_password, secure=True)
    message = sendgrid.Message((mail['from'], mail['from_name']), mail['subject'], mail['txt_body'], mail['html_body'])
    message.add_to(mail['to_address'], mail['to_name'])
    s.web.send(message)


def processMessage(message):
    strs = message.split('##')
    oiid = strs[0]
    full_name = strs[1]
    name = strs[2]
    email = strs[3]
    comments = strs[4]

    txt_mail = 'Invitation to Join Oi!'
    mail = read_file('/oiapp/mail.html')
    html_mail = mail.decode('utf-8') % (full_name, oiid, name, comments, oiid)
    subject = full_name + " wants to send you " + name
    mail = {'from': "info@oioi.me", 'from_name': 'Oi!', 'subject': subject, 'txt_body': txt_mail, 'html_body': html_mail, 'to_name': ''}
    mail['to_address'] = email
    send_invitation_mail(mail)

while True:
    #  Wait for next request from client
    message = socket.recv()
    print "Received request: ", message
    print processMessage(message)
    #  Do some 'work'
    time.sleep(1)  # Do some 'work'
    socket.send('ok')

