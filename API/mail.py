#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import current_app
import sendgrid
from API.utils import get_config_value
import re
from os.path import join, abspath, dirname
from pymongo import Connection



def is_oi_user(email):
    conn = Connection(get_config_value('MONGO_URL'))
    db = conn['oime']
    objects = db['users']
    u = objects.find_one({'$or': [{'sub_email': email.strip()}, {'username': email.strip()}]})
    if u is not None:
        return u
    return False



def read_file(filename):
    path = abspath(join(dirname(__file__), '.')) + filename
    print path
    f = open(path, 'r')
    return f.read()

def send_invitations(oi, full_name):
    txt_mail = 'Invitation to Join Oi!'
    mail = read_file('/oiapp/mail.html')
    html_mail = mail.decode('utf-8') % (full_name, oi['_id'], oi['name'], oi['comments'], oi['_id'])
    subject = full_name + " wants to invite you to join " + oi['name']
    mail = {'from': "info@oioi.me", 'from_name': 'Oi!', 'subject': subject, 'txt_body': txt_mail, 'html_body': html_mail, 'to_name': ''}
    for p in oi['invited']:
        # if is_valid_email(p):
        u = is_oi_user(p)
        if u:
            if u.get('mail_subscription', False):
                mail['to_address'] = p
                send_invitation_mail(mail)
        else:
            mail['to_address'] = p
            send_invitation_mail(mail)



def is_valid_email(email):
    if not re.match(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|edu|gov|uk|es|fr|de|cat|eu|mil|biz|info|mobi|name|aero|asia|jobs|museum)\b", email):
        return False
    return True


def send_invitation_mail(mail):

    current_app.logger.info('Mail sent to ' + mail['to_address'])
    sendgrid_user = get_config_value('SENDGRID_USER')
    sendgrid_password = get_config_value('SENDGRID_PASSWORD')
    s = sendgrid.Sendgrid(sendgrid_user, sendgrid_password, secure=True)
    message = sendgrid.Message((mail['from'], mail['from_name']), mail['subject'], mail['txt_body'], mail['html_body'])
    message.add_to(mail['to_address'], mail['to_name'])

    s.web.send(message)
