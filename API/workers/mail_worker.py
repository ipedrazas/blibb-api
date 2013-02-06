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
import time


parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.utils import get_config_value


print "URL Worker running at port 5558"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")


def read_file(filename):
    path = abspath(join(dirname(__file__), '.')) + filename
    print path
    f = open(path, 'r')
    return f.read()


def send_invitation_mail(mail):
    print 'Mail sent to ' + mail['to_address']
    sendgrid_user = get_config_value('SENDGRID_USER')
    sendgrid_password = get_config_value('SENDGRID_PASSWORD')
    s = sendgrid.Sendgrid(sendgrid_user, sendgrid_password, secure=True)
    message = sendgrid.Message((mail['from'], mail['from_name']), mail['subject'], mail['txt_body'], mail['html_body'])
    message.add_to(mail['to_address'], mail['to_name'])
    s.web.send(message)


def processMessage(message):
    txt_mail = 'Invitation to Join Oi!'
    # mail = read_file('/templates/mail.html')
    mail = read_file(message['template'])
    html_mail = mail.decode('utf-8') % (message['full_name'], message['comments'])
    subject = message['full_name'] + " wants to send you an Oi: " + message['name']
    mail = {'from': "info@oioi.me", 'from_name': 'Oi!', 'subject': subject, 'txt_body': txt_mail, 'html_body': html_mail, 'to_name': ''}
    mail['to_address'] = message['email']
    send_invitation_mail(mail)

while True:
    #  Wait for next request from client
    # message = socket.recv()
    msg = socket.recv_json()
    print str(msg)
    processMessage(msg)

    #  Do some 'work'
    time.sleep(1)  # Do some 'work'
    socket.send('ok')

socket.close()
context.term()
