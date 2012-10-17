#
#
##
#
#

import sendgrid
from flask import current_app
import re


def send_invites(owner, contacts):
    txt_mail = 'Invitation to Join Oi!'
    html_mail = 'Invitation to Join <b>Oi!</b>'
    subject = owner + " wants to invite you"
    mail = {'from': "info@oioi.me", 'from_name': 'Oi!', 'subject': subject, 'txt_body': txt_mail, 'html_body': html_mail, 'to_name': ''}
    for p in contacts:
        if is_valid_email(p):
            mail['to_address'] = p
            send_invitation_mail(mail)


def is_valid_email(email):
    if not re.match(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|edu|gov|mil|biz|info|mobi|name|aero|asia|jobs|museum)\b", email):
        return False
    return True


def send_invitation_mail(mail):

    sendgrid_user = current_app.config.get('SENDGRID_USER')
    sendgrid_password = current_app.config.get('SENDGRID_PASSWORD')
    s = sendgrid.Sendgrid(sendgrid_user, sendgrid_password, secure=True)
    message = sendgrid.Message((mail['from'], mail['from_name']), mail['subject'], mail['txt_body'], mail['html_body'])
    message.add_to(mail['to_address'], mail['to_name'])

    s.web.send(message)
